import dash
from dash import dcc, html


# # Function to read markdown from a file
# def read_markdown_file(path):
#     with open(path, 'r') as file:
#         return file.read()


markdown_content = '''

### Help Document 

###### **Login**
- Use the Project Id (PID) to login. 
    - Example: 'PID = '2023-S1-US-17' | Password = '1234''

###### **Job Management**
- After logging in, you will see a list of your previous jobs.
- You can also view current jobs on unity.

###### **Create a New Job**
- Click the "new job" button located on the top right of the account page.

###### **Session Management**
- Default session (`session-0`) and previous sessions will be displayed.
    - If `session-0` is selected, you can clone it:
        1. Click 'CLONE SESSION'.
        2. Input a number for the new session name.
    - If other sessions are selected, you can delete them:
        1. Click 'DELETE SESSION'.

###### **Runfile Management**
- After selecting a session, available runfiles will be displayed.
- Choose a runfile to view its content in the table.
    - The left corner shows the session and runfile name.
    - The right corner provides options to delete or clone the selected runfile.
    - The table shows the runfile content.Toggle columns to view less or more columns. Filter rows by typing in the filter cell
    - Click 'CLONE RUNFILE' to clone the selected runfile.

###### **Row Editing**
- Select a row to highlight it. Options for editing, deleting, and cloning will appear.
    - Click 'EDIT ROW' to modify row parameters and click 'Update' to save changes.
    - Click 'CLONE ROW' to modify the row parameters and click 'Save new row' to add it to the runfile table.

**Note:** The "SUBMIT JOB" button is currently set for a dry-run. Proper validation from the pipeline is pending.

'''


layout = html.Div(dcc.Markdown(markdown_content))
