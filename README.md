# TRAC_CSV_EXPORT_FOR_JIRA

Need Python 3.

You may have to update the trac environment:
trac-admin /path/to/projenv upgrade (let me remind you that Trac works on Python 2.7)

The paths to the files are set inside the script. Before importing the csv file, you must copy the ticket folder from the "files\attachments" folder to the special Jira folder - $JIRA_HOME/import/attachments (for example, C:\Program Files\Atlassian\Application Data\JIRA\import\attachments)

When importing a CSV file, you can make all the necessary field mappings and be sure to set the date format to "yyyy/MM/dd hh:mm:ss", for the type field the mapping is required.


