import dash
from dash import dcc, html

markdown_content = '''
#

### Help Document 

###### **Login**
Use the Project Id (PID) to login. 
- Example: 'PID = '2021-S1-US-3' | Password = '1234''
- If the password for the PID is not valid, an error message will be displayed.
###### **Session Management**
Default session (`session-0`) and previous sessions will be displayed.
- If `session-0` is selected, you can clone it:
    1. Click `CLONE SESSION`.
    2. Input a number for the new session name.
- If other session is selected, you can clone or delete it.

###### **Runfile Management**
- After selecting a session, available runfiles in this session will be displayed.
- Choose a runfile to view its content.
- The left corner shows the session and runfile name.
- The right corner provides `RUNFILE OPTIONS` to verify, edit, delete or clone the selected runfile.
    - Click `VERIFY` to verify the runfile content.
    - Click `DELETE` to delete the runfile.
    - Click `EDIT` to edit the runfile.
    - Click `CLONE` to clone the runfile.
    
###### **Table Management**
- After selecting a runfile and clicking `EDIT`, the runfile content will be displayed in a table.
- Click `TOGGLE COLUMNS` to view less or more columns. 
- Filter rows by typing in the filter cell
- Select a row or multiply rows and the `TABLE OPTIONS` dropdown menu will appear.
- Click `EDIT ROW`, the edit parameters layout will be displayed. Modify parameters and click `UPDATE` to save the changes.

'''

layout = html.Div(dcc.Markdown(markdown_content),
                  style={'margin-top': '50px', 'margin-left': '100px', 'margin-right': 'auto',
                         'text-align': 'left'})
