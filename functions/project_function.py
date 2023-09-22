import os
import shutil
from pathlib import Path
import dash_bootstrap_components as dbc
from flask_login import current_user
from dash import no_update, html, dcc
import pandas as pd
import subprocess
import json
import ast

default_time_range = [3, 7]


def get_work_lmt_path(config):
    work_lmt = os.environ.get('WORK_LMT')

    if work_lmt:
        print(f'account: WORK_LMT = {work_lmt}')
    elif 'path' in config and 'work_lmt' in config['path']:
        work_lmt = config['path']['work_lmt']
        print('Environment variable WORK_LMT not exists, get it from config.txt')
    else:
        print('Could not find the value of work_lmt')
        return None
    return work_lmt


def get_pid_lmtoy_path(work_lmt, username):
    return os.path.join(work_lmt, 'lmtoy_run', f'lmtoy_{username}')


def create_session_directory(WORK_LMT):
    pid_path = os.path.join(WORK_LMT, current_user.username)
    if not os.path.exists(pid_path):
        os.mkdir(pid_path)
    return pid_path


def check_user_exists():
    return current_user and current_user.is_authenticated


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
        files = find_runfiles(pid_lmtoy_path, username + '.')
        return [os.path.join(pid_lmtoy_path, file) for file in files]
    else:
        session_path = os.path.join(pid_path, session_name)
        files = find_runfiles(session_path, username + '.')
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
                            options=get_runfile_option(session['path']), )],
            title=session['name'], className='mb-2', item_id=session['name']
        )
        for session in session_info
    ]


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
        df.rename(columns={'obsnum': 'obsnum(s)'}, inplace=True)
    elif 'obsnums' in df.columns:
        df.rename(columns={'obsnums': 'obsnum(s)'}, inplace=True)
    return df


# save revised data to a runfile
# todo format each value and not write if there is no value for the column
def save_runfile(df, runfile_path):
    separator = '='
    lines = []
    for row in df.to_dict('records'):
        line = 'SLpipeline.sh'
        for column, value in row.items():
            if value is not None and str(value).strip()!='':
                line += f" {column}{separator}{value}"
        lines.append(line)
    with open(runfile_path, 'w') as f:
        f.write('\n'.join(lines))


def table_layout(table_data):
    output = table_data
    output[1] = table_data[1].split(',')
    # 1,2,3 to ['1', '2', '3']
    if output[3]:
        output[3] = table_data[3].split(',')
    if output[4]:
        output[4] = ast.literal_eval(output[4])

    for i in range(20, 25):
        print('table_data', table_data[i])
        if table_data[i] == '' or table_data[i] == '0':
            output[i] = 0
        else:
            output[i] = 1
    print('time range', output[4])
    return output


def layout_table(layout_data):
    output = layout_data
    output[1] = ",".join(layout_data[1])

    if output[3]:
        filtered_beam = filter(bool, layout_data[3])
        sorted_beam = sorted(filtered_beam, key=int)
        output[3] = ",".join(sorted_beam)
    else:
        output[3] = ''
    if output[4]:
        output[4] = f'[{layout_data[4]}]'

    for i in range(20, 25):
        print('layout_data', layout_data[i])
        if not layout_data[i]:
            output[i] = 0
        else:
            output[i] = 1
    return output


def create_modal(header_label, body_elements, footer_elements, modal_id, modal_head_id, ):
    return dbc.Modal(
        [
            dbc.ModalHeader(dbc.Label(header_label, className='custom-bold'), id=modal_head_id),
            dbc.ModalBody(body_elements),
            dbc.ModalFooter(footer_elements)
        ], id=modal_id, size='lg', centered=True, backdrop='static'
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


def get_highlight(selRow):
    """Return highlighting based on selected rows."""
    if selRow:
        return [{"if": {"row_index": i}, "backgroundColor": 'yellow'} for i in selRow]
    return no_update


def get_column_value(df, selected_row_idx, column_name):
    return df.loc[selected_row_idx, column_name] if column_name in df.columns else None
