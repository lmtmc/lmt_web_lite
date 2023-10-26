# lmt_web

## Introduction

This web application serves as an interface for managing pipeline jobs and configurations. Here are the instructions to get it up and running.


## Setup

### Environment and Dependencies

1. <b>Create a virtual environment, install the dependencies:
   ```
   make clean pjt
   ```
2. <b>Activate the virtual environment:
   ```
   source env/bin/activate
   ```
3. <b>make the config.txt:
   ```
    ./configure --with-work=work_lmt
4. <b>Optional</b>:<br>
   1.The repo includes a 'users.db'. If you want to create a new users.db or add a user,
   you can revise and run the code in users_mgt.py (needs more work for the database organization)<br>
   2.You can revise the config.txt file for file directories.<br>

## Run the App

1.  Run the Application by

    ```
    python3 app.py --port 8080
    ```

    The app will be running on http://127.0.0.1:8080 If you don't specify the port, it will default to http://127.0.0:8000

2.  If you run the app in a remote server, you can localforward it to your local machine by adding
    ```
    localforward 5000 127.0.0.1:8000
    ```
    in .ssh/config which will set up local port forwarding from port 5000 on your local
    machine to port 8000 on the remote server. And then open it using a web browser using the address of http://127.0.0.1:5000.


### Usage
###### **Login**
- Use the Project Id (PID) to login. 
    - Example: 'PID = '2023-S1-US-17' | Password = '1234'
    - Example: 'PID = '2023-S1-MX-3' | Password = '1234'

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
