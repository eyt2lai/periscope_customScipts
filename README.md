# periscope_customScripts

## Template Code for Bulk Updating User Permissions Across all Dashboards for a Single Role, in Sisense for Cloud Data Teams.

Hi There! Thanks for visiting this repo!

To give a little background about myself, I was a data analyst when I first started working with Periscope (now Sisense for Cloud Data Teams) - a business intelligence tool that facilitates quick analyses via allowing users to generate various visualizations from writing SQL against a database connection.

As part of a Data Robustness effort going on in my company, I embarked on a mission to clean up permissions across different roles in the tool.  

This project showcases a customizable version of some scripts that I used to automate the execution of this exercise. The code executes against the Sisense User and Role Management API (https://dtdocs.sisense.com/article/user-and-role-management-api-rbac).

If you use Periscope (Sisense for Cloud Data Teams) too, and are an analyst tasked with cleaning up permissions, hope you can find this useful!

By no means is this a perfect solution. What I would like to do as a next step is to "dockerize" the script so that instead of updating the variables within the individual script files themselves, they simply have to be inputted in a docker `run` command upon execution of the script.
