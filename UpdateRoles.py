import requests
import json
import pandas as pd
from pandas.io.json import json_normalize
from rolePrivileges import *
from roleDashboardPermissions import *

###############
## VARIABLES ##
###############

#API Variables
dashboards_url = 'https://api.periscopedata.com/api/v1/dashboards'
roles_url = 'https://api.periscopedata.com/api/v1/roles'
company_api_key = <company_api_key> # Input your company's Sisense for Cloud Data Teams API key
headers = {'HTTP-X-PARTNER-AUTH': company_api_key, 'Content-Type' : 'application/json'}

###############
## FUNCTIONS ##
###############

def get_dashboards_per_api_page(dashboards_url, headers):
    """Returns a list of all dashboard object IDs from a single page of Sisense's Dashboards API.
    :param url (str): Sisense's Dashboards API URL
    :param headers (dict): Default headers referenced in the API call
    :return: List
    """
    r = requests.get(dashboards_url, headers=headers)
    info = r.json()
    dashboard_object_list = []
    for i in info['dashboards']:
        dashboard_object_list.append(i['id'])

    dashboard_dict = {}
    for i in info['dashboards']:
        dashboard_dict[i['name']] = i['id']

    return info['next_page_start'], info['items_this_page'], dashboard_object_list, dashboard_dict


def get_all_dashboards(dashboards_url, headers):
    """Returns a list of all the dashboard object IDs from all pages of Sisense's Dashboards API.
    :param url (str): Sisense's Dashboards API URL
    :param headers (dict): Default headers referenced in the API call
    :return: List
    """
    n, i, d, v = get_dashboards_per_api_page(dashboards_url, headers) #'n' = dashboard_id indicating start of subsequent page in API
    new_dashboard_id_list = d
    new_dashboard_dict = v

    while n is not None:
        n, i, d, v = get_dashboards_per_api_page(dashboards_url+'?next_page_start='+n, headers)
        new_dashboard_id_list.extend(d)
        new_dashboard_dict.update(v)

    return new_dashboard_id_list, new_dashboard_dict


def get_role_ids_from_api(roles_url, headers):
    """Returns dictionary of 'role_name: role:id' pairs
    :param url (str): Sisense's Roles API URL
    :param headers (dict): Default headers referenced in the API call
    :return: Dictionary
    """
    r = requests.get(roles_url, headers=headers)
    info = r.json()
    roles_dict = {}
    for dict in info['roles']:
        roles_dict[dict['name']] = dict['id']
    return roles_dict


def bulk_update_dashboard_permissions_in_role(updater_email, headers, dashboards_to_update, role_name, test_mode, dashboard_permissions):
    """Bulk update dashboard permissions associated with a single, specified role, across specified dashboards. Doesn't update role privileges, name, or description.
    Relies on get_role_ids_from_apis() function to source role-specific ids.
    Relies on RolePrivileges.py file to source role-specific privileges.

    :param updater_email (str): Email of Company Admin updating permissions
    :param headers (dict): Default headers referenced in the API call
    :param dashboards_to_update (list): List of dashboards outputted from get_all_dashboards()
    :param role_name (str): Name of role
    :param test_mode (str): True or False; if false, permission updates are executed
    :param dashboard_permissions (list): New dashboard permissions for the role
    """
    permissions = []

    for id in dashboards_to_update: #dashboards_to_update is the list of dashboards returned from the get_all_dashboards() function
        dashboard_permissions_dict = {"object_type": "Dashboard", "object_id": id, "permissions": dashboard_permissions}
        permissions.append(dashboard_permissions_dict)
    print('New Bulk Permissions:', permissions)

    global payload
    global url
    if role_name == 'Data Analyst':
        payload = {"updated_by_email": updater_email, "privileges": data_analyst_privileges, "permissions": permissions}
        url = 'https://api.periscopedata.com/api/v1/roles/{0}'.format(data_analyst_role_id) + '?test_mode=' + test_mode
    elif role_name == 'Biz User':
        payload = {"updated_by_email": updater_email, "privileges": biz_user_privileges, "permissions": permissions}
        url = 'https://api.periscopedata.com/api/v1/roles/{0}'.format(biz_user_role_id) + '?test_mode=' + test_mode
    elif role_name == 'Everyone':
        payload = {"updated_by_email": updater_email, "privileges": everyone_privileges, "permissions": permissions}
        url = 'https://api.periscopedata.com/api/v1/roles/{0}'.format(everyone_role_id) + '?test_mode=' + test_mode
    #This role was created on the Sisense for Cloud Data Teams UI for testing purposes.
    elif role_name == 'Test':
        payload = {"updated_by_email": updater_email, "privileges": test_privileges, "permissions": permissions}
        url = 'https://api.periscopedata.com/api/v1/roles/{0}'.format(test_role_id) + '?test_mode=' + test_mode

    data = json.dumps(payload)
    response = requests.put(url, headers=headers, data=data)
    parsed = json.loads(response.text)
    print(json.dumps(parsed, indent=4, sort_keys=True))
    print('end')

def check_dashboard_permissions_per_role(roles_url, headers):
    """Returns dataframe of the roles + dashboard API details joined together.
    :param roles_url (str): Sisense's Roles API URL
    :param headers (dict): Default headers referenced in the API call
    """
    #Return roles_df
    roles_response = requests.get(roles_url, headers=headers)
    roles = json.loads(roles_response.text)
    roles_rough = json_normalize(roles['roles'])
    roles_df = json_normalize(roles['roles'], record_path=['permissions'], meta=['description','name'])
    final_roles_df = roles_df.rename(columns={'permissions':'dashboard_permissions','description':'role_description','name':'role_name'})
    print('Distinct Role Count Check: ', final_roles_df.role_name.nunique())

    #Return dashboards_df (Contains all dashboards)
    dashboard_object_ids, dashboard_name_id_dict = get_all_dashboards(dashboards_url, headers)
    dashboards_df = pd.DataFrame(list(dashboard_name_id_dict.items()), columns = ['dashboard_name','dashboard_id'])
    print('Distinct Dashboard Count Check: ', dashboards_df.dashboard_id.nunique())

    #Join roles_df with dashboards_df
    check_df = final_roles_df.merge(dashboards_df, how='left', left_on='object_id', right_on='dashboard_id')
    print('Merged Dashboard Count Check: ', check_df.dashboard_id.nunique())

####################
## CODE EXECUTION ##
####################

if __name__ == "__main__":

    # Returning the role_ids + role-specific privileges + role-specific dashboard permissions for each of the 3 standard roles created for the company.
    roles_dict = get_role_ids_from_api(roles_url, headers)

    data_analyst_role_id = roles_dict['Data Analyst']
    data_analyst_privileges = data_analyst_privileges
    data_analyst_dashboard_permissions = data_analyst_dashboard_permissions

    biz_user_role_id = roles_dict['Biz User'] #Somehow, a role_id doesn't show up unless you have manually added a single dashboard to the role
    biz_user_privileges = biz_user_privileges
    biz_user_dashboard_permissions = biz_user_dashboard_permissions

    everyone_role_id = roles_dict['Everyone']
    everyone_privileges = everyone_privileges
    everyone_dashboard_permissions = everyone_dashboard_permissions

    test_role_id = roles_dict['Test']
    test_privileges = test_privileges
    test_dashboard_permissions = test_dashboard_permissions

    ##################################################################
    # Setting the variables for the bulk dashboard permission update #
    ##################################################################
    updater_email = <updater@company.com> #Change to the email of whichever Admin is making the updates
    role_name = <Everyone> #Change to any 1 of the existing Sisense roles you want to update all dashboards for (Reference the exact role name in Sisense)
    test_mode = 'true' #Change test mode to 'false' when you want to implement the changes (not just test them)
    role_privileges = everyone_privileges #Change to the privileges variable associated with the role for which you want to update all dashboard permissions
    dashboard_permissions = everyone_dashboard_permissions

    ##################################################
    ## NO NEED TO CHANGE ANY VARIABLE VALUES BELOW: ##
    ##################################################
    # Returning list of all dashboards in existence
    n,i,d,v = get_dashboards_per_api_page(dashboards_url, headers)
    a,b = get_all_dashboards(dashboards_url, headers)
    complete_dashboard_id_list = a
    complete_dashboard_dict = b

    # Determining the list of dashboards for which to bulk update permissions
    dashboards_to_update = complete_dashboard_id_list
    print('Number of Dashboards for Bulk Permission Update: ', len(dashboards_to_update))

    #Executing the bulk dashboard permissions update for the specified role + specified list of dashboards
    bulk_update_dashboard_permissions_in_role(updater_email, headers, dashboards_to_update, role_name, test_mode, dashboard_permissions)
    check_dashboard_permissions_per_role(roles_url, headers)
