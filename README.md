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

### Login

- Use the Project ID (PID) to log in.
  - Examples:
    - PID: `2023-S1-US-17` | Password: `1234`
    - PID: `2023-S1-MX-3` | Password: `1234`


### Create a New Job

- Initiate new job creation by clicking the "new job" button on the account page.

### Session Management

- Manage your sessions. The default session (`session-0`) and other sessions are available.
  - Clone `session-0` by clicking 'CLONE SESSION' and providing a new session number.
  - Delete non-default sessions by selecting them and clicking 'DELETE SESSION'.

### Runfile Management

- Select a session to view and manage runfiles.
  - Options for runfile cloning or deletion are available.
  - View runfile content in a table layout, with flexible viewing options.

### Row Editing

- Engage with content directly by selecting rows for editing, cloning, or deletion.
  - Save changes or new entries efficiently.

**Note:** The "SUBMIT JOB" feature is in dry-run mode. Integration with the pipeline for validation is pending further development.
