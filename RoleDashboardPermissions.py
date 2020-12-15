"""
This file contains the dashboard permissions associated with each custom role created in Sisense.
Update the permissions as desired.
"""

#Role Name = Data Analyst
data_analyst_dashboard_permissions = ['read_dashboards', 'create_discovery_charts', 'create_sql_charts', 'edit_chart_as_copy'
                                    , 'edit_dashboard_settings', 'clone_dashboards', 'archive_dashboards'
                                    , 'download_pdf', 'shared_dashboards', 'email_reports']

#Role Name = Biz User
biz_user_dashboard_permissions = ['read_dashboards', 'create_discovery_charts', 'create_sql_charts', 'edit_chart_as_copy'
                                 , 'download_pdf', 'shared_dashboards', 'email_reports']

#Role Name = Everyone
everyone_dashboard_permissions = []
