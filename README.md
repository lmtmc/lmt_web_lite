# lmt_web

## Introduction

This web application serves as an interface for managing pipeline jobs and configurations. Here are the instructions to get it up and running.

## Requirements 

Ensure LMTOY is installed and accessible on your system. Then configure it to make a valid config.txt:

      ./configure

under rare circumstances you might need to run something like

      ./configure --with-work=/home/lmt/work_lmt

but normally your $WORK_LMT environment variable from LMTOY is used during the configure stage. During run-time again any 
present $WORK_LMT will be used, but if not, the value in config.txt will be used.

## Setup

### Environment and Dependencies

1. <b>Create a virtual environment:</b> </br>
   python3 -m venv env
2. <b>Activate the virtual environment:</b> <br>
   source env/bin/activate
3. <b>Install the required packages:</b> <br>
   pip install -r requirements.txt <br>
   <b>Note:</b> Make sure the versions of FLask-SQLAlchemy and SQLAlchemy are like below. 
   Flask-SQLAlchemy==2.5.1
   SQLAlchemy==1.4.36
4. <b>Optional</b>:<br>
   1.The repo includes a 'users.db'. If you want to create a new users.db or add a user, 
   you can revise and run the code in users_mgt.py (needs more work for the database organization)<br>
   2.You can revise the config.txt file for file directories.<br>
   
## Run the App

   1. Start the Application by **python3 app.py**. The app will be running on http://127.0.0.1:8000
   2. If you run the app in a remote server, you can localforward it to your local machine by adding
   'localforward 5000 127.0.0.1:8000' in .ssh/config which will set up local port forwarding from port 5000 on your local
   machine to port 8000 on the remote server. And then open it using a web browser using the address of http://127.0.0.1:5000. 
   3. If you want to change the port that the app is running on, go the bottom of "app.py" and change port='8000' to your desired number.

### Usage

1. <b>Login:</b></br>
   Use the ProjectId (PID) for login. E.g.,<br>
   PID = '2023-S1-US-17' Password = '1234' <br>
   PID = '2021-S1-MX-3' Password = '1234'
2. <b>Job Management:</b><br>
   Once logged in, you will see a list of the users' previous jobs. You can also view the current jobs on unity.
3. <b>Create a new job</b><br>
   click "new job" button on the top right. 
4. <b>Session</b><br>
   The previous sessions or default session will appear. <br>
   Clone a session by selecting it and clicking 'CLONE SESSION'. (If there's no session selected,
   the new session will not be cloned. Here needs a message to remind the user). <br>
   The input name has to start with 'session'.
5. <b>Runfile</b><br>
   Once selected one of the sessions, the available runfiles will appear. <br>
   Choose one of the runfiles, which will then display will its content in the table. <br> 
   On the left corner of the table there are the session and name of the runfile.
   On the right corner of the table there are buttons for deleting and cloning the selected runfile.<br>
6. <b>Row editing</b><br>
   Select a row, it highlights, and the options to edit, delete and clone appear.<br>
   Edit the row parameters and click 'Update' to save changes.<br>
   Clone and edit the row parameter and click 'Save new row' to add a new row. <br>
7. The "SUBMIT JOB" button currently performs a simply dry-run function (need validation functions from the pipeline)

## Next step:

1. <b>Data validation:</b>
2. <b>Exam each parameter in detail.</b> 
   1. source: can't be none and exists for each runfile?
   2. obsnums: multiply selections, can it be none?
   3. bank: only available for some projects?
   4. Time Range: define min, max, step values?
   5. Resolution (pix_list): better way to display?
   6. And so on...
