# LMT Web

## Introduction

This web application serves as an interface for managing pipeline jobs and configurations. The sections below provide instructions on setting up and running the application.

## Setup

### Environment and Dependencies

Follow these steps to set up your environment and install necessary dependencies:

1. **Create a virtual environment and install the dependencies:**
    ```shell
    make clean pjt
    ```

2. **Activate the virtual environment:**
    ```shell
    source env/bin/activate
    ```

3. **Create the config.txt file:**
    ```shell
   autoconf
    ./configure --with-work=work_lmt
    ```

4. **Optional Steps:**
    - The repository includes a 'users.db'. If you wish to create a new 'users.db' or add a user, consider revising and running the code in `users_mgt.py`. Further enhancements for the database organization may be required.
    - You may modify the `config.txt` file to specify different file directories.

## Running the Application

1. **Start the application:**
    ```shell
    python3 app.py --port 8080
    ```
    The application will be accessible at [http://127.0.0.1:8080](http://127.0.0.1:8080). If you don't specify a port, the default address will be [http://127.0.0.1:8000](http://127.0.0.1:8000).

2. **Setting up on a remote server:**
    - If you are running the application on a remote server, consider using local port forwarding. Add the following configuration to your `.ssh/config`:
        ```shell
        LocalForward 5000 127.0.0.1:8000
        ```
    - This configuration forwards the local port 5000 to port 8000 on your remote server. You can then access the application using [http://127.0.0.1:5000](http://127.0.0.1:5000) in your local web browser.

## Usage

### **Login**
Use the Project Id (PID) to login. 
- Example: 'PID = '2021-S1-US-3' | Password = '1234''
- If the password for the PID is not valid, an error message will be displayed.


### **Session Management**
Default session (`session-0`) and previous sessions will be displayed.
- If `session-0` is selected, you can clone it:
    1. Click `CLONE SESSION`.
    2. Input a number for the new session name.
- If other session is selected, you can clone or delete it.

### **Runfile Management**
- After selecting a session, available runfiles in this session will be displayed.
- Choose a runfile to view its content.
- The left corner shows the session and runfile name.
- The right corner provides `RUNFILE OPTIONS` to verify, edit, delete or clone the selected runfile.
    - Click `VERIFY` to verify the runfile content.
    - Click `DELETE` to delete the runfile.
    - Click `EDIT` to edit the runfile.
    - Click `CLONE` to clone the runfile.
    
### **Table Management**
- After selecting a runfile and clicking `EDIT`, the runfile content will be displayed in a table.
- Click `TOGGLE COLUMNS` to view less or more columns. 
- Filter rows by typing in the filter cell
- Select a row or multiply rows and the `TABLE OPTIONS` dropdown menu will appear.
- Click `EDIT ROW`, the edit parameters layout will be displayed. Modify parameters and click `UPDATE` to save the changes.