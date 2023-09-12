import os
import shutil
from pathlib import Path
import dash_bootstrap_components as dbc
from flask_login import current_user
from dash import no_update
import pandas as pd
import subprocess
import json


# Functions
def ensure_path_exists(path):
    if not path or not os.path.exists(path):
        return False
    return True


def load_source_data(file_name):
    with open(file_name, 'r') as json_file:
        data = json.load(json_file)
    return data


# find files with prefix
def find_files(folder_path, prefix):
    return sorted([filename for filename in os.listdir(folder_path) if filename.startswith(prefix)])


def find_runfiles(folder_path, prefix):
    matching_files = find_files(folder_path, prefix)
    if not matching_files:
        print("No matching files found. Running 'mk_runs.py'")
        subprocess.run(["python3", "mk_runs.py"])
        matching_files = find_files(folder_path, prefix)
        if matching_files:
            print(f"Matching files: {matching_files}")
        else:
            print("No matching files found even after running 'mk_runs.py'")
    return matching_files


# Function to find and construct file paths
def construct_file_paths(init_session, session_name, pid_path, pid_lmtoy_path, username):
    if session_name == init_session:
        files = find_runfiles(pid_lmtoy_path, username+'.')
        return [os.path.join(pid_lmtoy_path, file) for file in files]
    else:
        session_path = os.path.join(pid_path, session_name)
        files = find_runfiles(session_path, username+'.')
        return [os.path.join(session_path, file) for file in files]


# get the session names and their paths in a folder
def get_session_info(default_session, pid_path):
    default_session_path = os.path.join(os.path.dirname(pid_path), 'lmtoy_run', f'lmtoy_{current_user.username}')
    session_info = [{'name': default_session, 'path': default_session_path}]

    if ensure_path_exists(pid_path):
        new_sessions = [
            {'name': file, 'path': os.path.join(pid_path, file)}
            for file in sorted(os.listdir(pid_path))
            if file.startswith('session')
        ]

        session_info.extend(new_sessions)

    return session_info


def get_runfile_option(session_path):
    matching_files = find_runfiles(session_path, f'{current_user.username}.')
    return [{'label': label, 'value': f'{session_path}/{label}'} for label in matching_files]


def get_session_list(default_session, pid_path):
    session_info = get_session_info(default_session, pid_path)
    return [
        dbc.AccordionItem(
            [dbc.RadioItems(id={'type': 'runfile-radio', 'index': session['name']},
                            options=get_runfile_option(session['path']))],
            title=session['name'], className='mb-2', item_id=session['name']
        )
        for session in session_info
    ]


# def clone_session(pid_path, name, original_session):
#     if not name:
#         return False, "Please input a name!"
#     if not name.startswith("session"):
#         return False, f"Please input a name start with session"
#
#     new_session_path = os.path.join(pid_path, name)
#     # Check if the session directory already exists
#     if os.path.exists(new_session_path):
#         # If the directory not exist, create it
#         return False, f'Session {name} already exists'
#     os.mkdir(new_session_path)
#     original_session_path = os.path.join(pid_path, original_session, 'lmtoy_run')
#     new_session = os.path.join(new_session_path, 'lmtoy_run')
#     shutil.copytree(original_session_path, new_session)
#     return True, f"Folder {name} created successfully!"

def clone_session(pid_path, name, original_path):
    if not name:
        return False, "Please input a name!"
    if not name.startswith("session"):
        return False, f"Please input a name start with session"

    new_session_path = os.path.join(pid_path, name)
    # Check if the session directory already exists
    if os.path.exists(new_session_path):
        # If the directory not exist, create it
        return False, f'Session {name} already exists'
    os.mkdir(new_session_path)
    for file in original_path:
        shutil.copy(file, new_session_path)
    return True, f"Folder {name} created successfully!"


def clone_runfile(runfile, name):
    if not name:
        return False, "Please input a name!"
    new_name_path = os.path.join(Path(runfile).parent, name)
    # Check if the session directory already exists
    if os.path.exists(new_name_path):
        # If the directory not exist, create it
        return True, f'Runfile {name} already exists'
    shutil.copy(runfile, new_name_path)
    return True, f"Runfile {name} created successfully!"


def del_session(folder_path):
    # Check if the folder exists
    if os.path.exists(folder_path):
        # If it exists, delete the folder and all its contents
        shutil.rmtree(folder_path)
        return False, f"The folder {folder_path} has been deleted successfully."
    else:
        print(f"The folder {folder_path} does not exist.")


# helper function for session display
def handle_new_session():
    return True, ''


def handle_save_session(init_session, active_session, pid_path, pid_lmtoy_path, name):
    file_path = construct_file_paths(init_session, active_session, pid_path, pid_lmtoy_path, current_user.username)
    [session_added, message] = clone_session(pid_path, name, file_path)
    return not session_added, message


def handle_delete_session(pid_path, active_session):
    session_path = os.path.join(pid_path, active_session)
    del_session(session_path)
    return "Session deleted successfully"


def handle_delete_runfile(stored_data):
    del_runfile(stored_data['runfile'])
    return "Runfile deleted successfully"


def del_runfile(runfile):
    # Check if the file exists
    if os.path.exists(runfile):
        # If it exists, delete the folder and all its contents
        os.remove(runfile)
        return False, f"The file {runfile} has been deleted successfully."
    else:
        print(f"The file {runfile} does not exist.")


def add_runfile(runfile_path, name):
    new_runfile_path = os.path.join(runfile_path, name)
    # Attempt to create the new runfile
    try:
        open(new_runfile_path, 'x').close()
        return True, f"Runfile {name} has been created successfully."
    except FileExistsError:
        # If the runfile already exists, inform the user
        return False, f'Runfile {name} already exists at {runfile_path}'


def initialize_common_variables(runfile, selRow, init_session):
    df = df_runfile(runfile)
    runfile_title = get_runfile_title(runfile, init_session)
    highlight = get_highlight(selRow)
    return df, runfile_title, highlight


# def generate_runfile_option(pid_path):
#     session_names = get_session_info(pid_path).keys()
#     return {session_name: get_runfile_option(pid_path + f'/{session_name}/lmtoy_run/lmtoy_{current_user.username}')
#             for session_name in session_names}


def df_runfile(filename):
    data = []
    if os.path.exists(filename):
        with open(filename) as file:
            for line in file:
                commands = line.strip().split()
                row = {command.split('=')[0]: command.split('=')[1] for command in commands if '=' in command}
                data.append(row)
    df = pd.DataFrame(data)
    # rename obsnum to obsnum(s)
    if 'obsnum' in df.columns:
        df.rename(columns={'obsnum':'obsnum(s)'}, inplace=True)
    elif 'obsnums' in df.columns:
        df.rename(columns={'obsnums':'obsnum(s)'}, inplace=True)
    return df


# save revised data to a runfile
def save_runfile(df, runfile_path):
    separator = '='
    lines = []
    for row in df.to_dict('records'):
        line = 'SLpipeline.sh'
        for column, value in row.items():
            line += f" {column}{separator}{value}"
        lines.append(line)
    with open(runfile_path, 'w') as f:
        f.write('\n'.join(lines))


def create_modal(header_label, body_elements, footer_elements, modal_id, size='lg', centered=True):
    return dbc.Modal(
        [
            dbc.ModalHeader(dbc.Label(header_label, className='custom-bold')),
            dbc.ModalBody(body_elements),
            dbc.ModalFooter(footer_elements)
        ], id=modal_id, size=size, centered=centered
    )


def dry_run(runfile):
    df = df_runfile(runfile)
    message = 'Submitted!'
    color = 'success'
    if 'admit' in df.columns:
        if not all(x in ['0', '1'] for x in df['admit']):
            message = 'Please input 0 or 1 for in the admit field!'
            color = 'danger'
    return message, color


def first_file_path(folder_path):
    try:
        files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
        if files:
            first_file = files[0]
            first_file_path = os.path.join(folder_path, first_file)
            return first_file_path
        else:
            return None
    except FileNotFoundError:
        print("Folder not found")
        return None


def get_runfile_title(runfile_path, init_session):
    parts = runfile_path.split('/')
    session_string = next((part for part in parts if 'session' in part), init_session)
    runfile_title = os.path.basename(runfile_path)
    return f'{session_string}: {runfile_title}'


def get_selected_runfile(ctx, data_store):
    """Determine the selected runfile based on trigger."""
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
    if 'runfile-radio' in trigger_id:
        return ctx.triggered[0]['value']
    elif data_store.get('runfile') and os.path.exists(data_store['runfile']):
        return data_store['runfile']
    return None


# def get_dataframe_and_columns(selected_runfile):
#     """Return DataFrame and columns based on selected runfile."""
#     df = df_runfile(selected_runfile)
#     columns = [{'name': col, 'id': col, 'deletable': False, 'hideable': True} for col in df.columns]
#     return df, columns


def get_highlight(selRow):
    """Return highlighting based on selected rows."""
    if selRow:
        return [{"if": {"row_index": i}, "backgroundColor": "yellow"} for i in selRow]
    return no_update


def get_column_value(df, selected_row_idx, column_name):
    return df.loc[selected_row_idx, column_name] if column_name in df.columns else None
