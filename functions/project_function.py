import os
import shutil
import sys
from pathlib import Path
import dash_bootstrap_components as dbc
from flask_login import current_user
from dash import no_update, html, dcc
import pandas as pd
import subprocess
import json
import ast
import re
import time
from functions import logger

logger = logger.logger


# Function to get pid options from the given path
def get_pid_option(path):
    result = []
    for folder_name in os.listdir(path):
        full_path = os.path.join(path, folder_name)

        if os.path.isdir(full_path) and folder_name.startswith('lmtoy_'):
            label_value = os.path.basename(folder_name.split('_')[1])
            result.append({'label': label_value, 'value': label_value})

    return result


def get_work_lmt_path(config):
    work_lmt = os.environ.get('WORK_LMT')

    if work_lmt:
        print(f'login: WORK_LMT = {work_lmt}')
    elif 'path' in config and 'work_lmt' in config['path']:
        work_lmt = config['path']['work_lmt']
        print('Environment variable WORK_LMT not exists, get it from config.txt')
    else:
        print('Could not find the value of work_lmt')
        return None
    return work_lmt


# def create_session_directory(WORK_LMT):
#     pid_path = os.path.join(WORK_LMT, current_user.username)
#     if not os.path.exists(pid_path):
#         os.mkdir(pid_path)
#     return pid_path


def check_user_exists():
    return current_user and current_user.is_authenticated


# check if path exists
def ensure_path_exists(path):
    if not path or not os.path.exists(path):
        print(f"Path {path} does not exist")
        return False
    print(f"Path {path} exists")
    return True


def load_source_data(file_name):
    with open(file_name, 'r') as json_file:
        data = json.load(json_file)
    return data


def process_cmd(commands):
    for cmd in commands:
        process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = process.communicate()
        if process.returncode != 0:
            print(f"Error executing command: {cmd}")
            print(err.decode('utf-8'))
        else:
            print(out.decode('utf-8'))


# find files with prefix
def find_files(folder_path, prefix):
    if not folder_path:
        raise ValueError("The provided folder path is empty or None.")

    if not os.path.exists(folder_path):
        raise FileNotFoundError(f"No such directory: {folder_path}")

    files = [filename for filename in os.listdir(folder_path) if
             os.path.isfile(os.path.join(folder_path, filename)) and filename.startswith(prefix)]
    return sorted(files)


def find_runfiles(folder_path, prefix):
    matching_files = find_files(folder_path, prefix)
    if not matching_files:
        print("No matching files found. Running 'mk_runs.py'")

        matching_files = find_files(folder_path, prefix)
        if matching_files:
            print(f"Matching files: {matching_files}")
        # else:
        #     my_runs.mk_runs()
        #     time.sleep(1)
        #     print("No matching files found even after running 'mk_runs.py'")
    return matching_files


def get_source(default_work_lmt, pid):
    pid_path = os.path.join(default_work_lmt, 'lmtoy_run', f'lmtoy_{pid}')
    json_file = os.path.join(pid_path, 'source.json')
    if os.path.exists(json_file):
        json_data = load_source_data(json_file)
        sources = json_data
    else:
        logger.info(f'No source.json file found in {pid_path}, executing mk_runs.py to generate the sources')
        mk_runs_file = os.path.join(pid_path, 'mk_runs.py')
        result = subprocess.run(['/home/lmt/lmt_web_lite/env/bin/python3', mk_runs_file], capture_output=True,
                                text=True, cwd=pid_path)

        # checks if the command ran successfully(return code 0)
        if result.returncode == 0:
            output = result.stdout  # converts the stdout string to a regular string
        else:
            output = result.stderr  # convert the error message to a string
        pattern = r"(\w+)\[\d+/\d+\] : ([\d,]+)"
        matches = re.findall(pattern, output)
        # sources = {name: list(map(int, obsnums.split(','))) for name, obsnums in matches}
        sources = {name: [int(x) for x in obsnums.split(',')] for name, obsnums in matches}
    return sources


# get the session names and their paths in a folder
def get_session_info(default_session, pid_path):
    default_session_path = os.path.join(os.path.dirname(pid_path), 'lmtoy_run', f'lmtoy_{current_user.username}')
    session_info = [{'name': default_session, 'path': default_session_path}]

    if ensure_path_exists(pid_path):
        new_sessions = [
            {'name': file, 'path': os.path.join(pid_path, file, 'lmtoy_run', f'lmtoy_{current_user.username}')}
            for file in sorted(os.listdir(pid_path))
            if file.startswith('Session')
        ]

        session_info.extend(new_sessions)
    return session_info


def get_runfile_option(session_path):
    matching_files = find_runfiles(session_path, f'{current_user.username}.')
    return [{'label': label, 'value': f'{session_path}/{label}'} for label in matching_files]


def get_session_list(default_session, pid_path):
    session_info = get_session_info(default_session, pid_path)
    print('session_info', session_info)
    return [
        dbc.AccordionItem(
            [dbc.RadioItems(id={'type': 'runfile-radio', 'index': session['name']},
                            options=get_runfile_option(session['path']),
                            className='my-radio-items', inline=True)],
            title=session['name'], className='mb-2', item_id=session['name'],
        )
        for session in session_info
    ]

    # def handle_save_session(pid_path, name):
    #     print('name', name)
    #     if not name:
    #         return True, "Please input a session number!"
    #     new_session_name = f'Session-{name}'
    #     new_session_path = os.path.join(pid_path, new_session_name)
    #     # Check if the session directory already exists
    #     if os.path.exists(new_session_path):
    #         # If the directory not exist, create it
    #         return True, f'{new_session_name} already exists'

    # os.environ['WORK_LMT'] = new_session_path
    # os.environ['PID'] = current_user.username
    #
    # # use lmtoy_run the clone PID to a new session
    # commands = [
    #     'mkdir -p $WORK_LMT'
    #     'cd $WORK_LMT',
    #     'lmtoy_run $PID'
    # ]
    # process_cmd(commands)
    return False, f'{new_session_name} created successfully!'


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


# def handle_save_session(init_session, active_session, pid_path, pid_lmtoy_path, name):
#     file_path = construct_file_paths(init_session, active_session, pid_path, pid_lmtoy_path, current_user.username)
#     [session_added, message] = clone_session(pid_path, name, file_path)
#     return not session_added, message

def handle_delete_session(pid_path, active_session):
    session_path = os.path.join(pid_path, active_session)
    del_session(session_path)
    return "Session deleted successfully!"


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
        logger.info(f'{filename} exists')
        try:
            with open(filename) as file:
                content = file.read()
                # logger.debug(f'Content of {filename}:\n {content}')
                file.seek(0)
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
            # logger.info(f'Final DataFrame with renamed columns: \n {df}')
            # rename pix_list to exclude_beams
            if 'pix_list' in df.columns:
                df.rename(columns={'pix_list': 'exclude_beams'}, inplace=True)
            return df
        except Exception as e:
            logger.error(e)
    else:
        logger.warning(f'{filename} does not exist')
    return pd.DataFrame()


# save revised data to a runfile
# todo format each value and not write if there is no value for the column
def save_runfile(df, runfile_path):
    separator = '='
    lines = []
    for row in df.to_dict('records'):
        line = 'SLpipeline.sh'
        for column, value in row.items():
            if value is not None and str(value).strip() != '':
                if column == 'obsnum(s)':
                    print('print value', value)
                    if ',' in value:
                        column = 'obsnums'
                    else:
                        column = 'obsnum'
                if column == 'exclude_beams':
                    column = 'pix_list'
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

        if table_data[i] == '' or table_data[i] == '0':
            output[i] = 0
        else:
            output[i] = 1

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

        if not layout_data[i]:
            output[i] = 0
        else:
            output[i] = 1
    return output


def create_modal(header_label, body_elements, footer_elements, modal_id):
    return dbc.Modal(
        [
            dbc.ModalHeader(dbc.Label(header_label, className='custom-bold')),
            dbc.ModalBody(body_elements),
            dbc.ModalFooter(footer_elements)
        ], id=modal_id, size='lg', centered=True, backdrop='static', scrollable=True
    )


def dry_run(runfile):
    df = df_runfile(runfile)
    message = 'Submitted!'
    color = 'success'
    # if 'admit' in df.columns:
    #     if not all(x in ['0', '1'] for x in df['admit']):
    #         message = 'Please input 0 or 1 for in the admit field!'
    #         color = 'danger'
    message = f'runs.verify(\'bench1.run\')'
    # if message is None:
    #     message = 'Submitted!'
    #     color = 'success'
    # else:
    #     message = message
    #     color = 'danger'
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
    session_string = next((part for part in parts if 'Session' in part), init_session)
    runfile_title = os.path.basename(runfile_path)
    return f'{session_string}: {runfile_title}'


def get_selected_runfile(ctx):
    """Determine the selected runfile based on trigger."""
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
    if 'runfile-radio' in trigger_id:
        return ctx.triggered[0]['value']
    # elif data_store.get('runfile') and os.path.exists(data_store['runfile']):
    #     return data_store['runfile']
    return None


def get_highlight(selRow):
    """Return highlighting based on selected rows."""
    if selRow:
        return [{"if": {"row_index": i}, "backgroundColor": 'yellow'} for i in selRow]
    return no_update


def get_column_value(df, selected_row_idx, column_name):
    return df.loc[selected_row_idx, column_name] if column_name in df.columns else None


def display_row_details(details_data):
    # Divide the dictionary into 6 equal parts
    n = len(details_data)
    part_size = n // 6 + (1 if n % 6 else 0)  # Calculate size of each part, considering remainder
    dict_parts = [dict(list(details_data.items())[i:i + part_size]) for i in range(0, n, part_size)]
    columns = []
    for part in dict_parts:
        rows = []
        for key, value in part.items():
            row = html.Div([
                html.Div(f"{key}:", className='col-6', style={'font-weight': 'bold'}),  # bold the key
                html.Div(str(value) if value else "-", className='col-6'),
            ], className='row mb-2')
            rows.append(row)
        column = html.Div(rows, className='col-md-2')  # Adjust for 6 columns
        columns.append(column)

    return html.Div(columns, className='row')

#
# def edit_row_details(details_data):
# Divide the dictionary into 6 equal parts
# n = len(details_data)
# part_size = n // 6 + (1 if n % 6 else 0)  # Calculate size of each part, considering remainder
# dict_parts = [dict(list(details_data.items())[i:i + part_size]) for i in range(0, n, part_size)]
# columns = []
# for part in dict_parts:
#     rows = []
#     for key, value in part.items():
#         row = html.Div([
#             html.Div(f"{key}:", className='col-6', style={'font-weight': 'bold'}),  # bold the key
#             html.Div(str(value) if value else "-", className='col-6'),
#         ], className='row mb-2')
#         rows.append(row)
#     column = html.Div(rows, className='col-md-2')  # Adjust for 6 columns
#     columns.append(column)

# return html.Div(edit_parameter.)
