import os
import shutil
import threading
from pathlib import Path
import dash_bootstrap_components as dbc
from flask_login import current_user
from dash import no_update, html, dcc
import pandas as pd
import subprocess
import json
import ast
import re
import plotly.graph_objects as go
from functions import logger
from lmtoy_lite.lmtoy import runs
from config import config
logger = logger.logger

python_path = config['path']['python_path']
lmtoy_path = config['path']['lmtoy_path']
script_path = config['path']['script_path']


if not os.path.exists(script_path):
    raise FileNotFoundError(f"File not found: {script_path}")
def set_pythonpath():
    current_pythonpath = os.environ.get('PYTHONPATH') or ''
    new_path = lmtoy_path
    if new_path not in current_pythonpath:
        if current_pythonpath:
            updated_pythonpath = f"{new_path}:{current_pythonpath}"
        else:
            updated_pythonpath = new_path
        os.environ['PYTHONPATH'] = updated_pythonpath
set_pythonpath()

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
    # # Extract the part after the last dot in each file name
    # files_after_dot = [filename.split('.')[-1] for filename in files if '.' in filename]

    return sorted(files)


def find_runfiles(folder_path, prefix):
    matching_files = find_files(folder_path, prefix)
    if not matching_files:
        print("No matching files found. Running 'mk_runs.py'")

        matching_files = find_files(folder_path, prefix)
        if matching_files:
            print(f"Matching files: {matching_files}")
    return matching_files


def make_tooltip(content, target):
    return html.Div(dbc.Tooltip(content, target=target, className='large-tooltip', placement='bottom'))


def get_source(default_work_lmt, pid):
    pid_path = os.path.join(default_work_lmt, 'lmtoy_run', f'lmtoy_{pid}')
    json_file = os.path.join(pid_path, f'{pid}_source.json')
    if os.path.exists(json_file):
        json_data = load_source_data(json_file)
        sources = json_data
    else:
        logger.info(f'No source.json file found in {pid_path}, executing mk_runs.py to generate the sources')
        mk_runs_file = os.path.join(pid_path, 'mk_runs.py')
        # result = subprocess.run(['/home/lmt/LMT_projects/lmt_web_new/lmt_web_lite/env/bin/python3', mk_runs_file], capture_output=True,
        #                         text=True, cwd=pid_path)
        result = subprocess.run([python_path, mk_runs_file], capture_output=True,
                                text=True, cwd=pid_path)
        print(f"result: {result}")
        # checks if the command ran successfully(return code 0)
        if result.returncode == 0:
            output = result.stdout  # converts the stdout string to a regular string
        else:
            output = result.stderr  # convert the error message to a string
        pattern = r"(\w+)\[\d+/\d+\] : ([\d,]+)"
        matches = re.findall(pattern, output)
        # sources = {name: list(map(int, obsnums.split(','))) for name, obsnums in matches}
        sources = {name: [int(x) for x in obsnums.split(',')] for name, obsnums in matches}
    print(f'sources: {sources}')
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
    return [
        dbc.AccordionItem(
            [dbc.RadioItems(id={'type': 'runfile-radio', 'index': session['name']},
                            options=get_runfile_option(session['path']),
                            # className='my-radio-items',
                            inline=True
                            )],
            title=session['name'], className='mb-2', item_id=session['name'],
        )
        for session in session_info
    ]
    return False, f'{new_session_name} created successfully!'


def clone_runfile(runfile, name):
    if not name:
        return False, "Please input a name!"
    new_name_path = os.path.join(Path(runfile).parent, name)
    print(f'new_name_path: {new_name_path}')
    # Check if the session directory already exists
    if os.path.exists(new_name_path):
        # If the directory not exist, create it
        return True, f'Runfile {name} already exists', True
    shutil.copy(runfile, new_name_path)
    return False, f"Runfile {name} created successfully!", False


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


def handle_delete_session(pid_path, active_session):
    session_path = os.path.join(pid_path, active_session)
    del_session(session_path)
    return "Session deleted successfully!"


def handle_delete_runfile(stored_data):
    del_runfile(stored_data['runfile'])
    return "Runfile deleted successfully"

def current_file(selected_runfile):
    return next((value for value in selected_runfile if value), None)
def del_runfile(runfile):
    # Check if the file exists
    if os.path.exists(runfile):
        # If it exists, delete the folder and all its contents
        print(f"Deleting the file {runfile}")
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


def update_df_with_state_values(df, selected_rows, state_values, table_column):
    # Log or print the DataFrame and selected rows for debugging
    print("Before update:")
    print(df)
    print("Selected rows:", selected_rows)

    for i, column in enumerate(table_column[2:]):
        if state_values[i + 2] is not None and state_values[i + 2] != []:
            value = state_values[i + 2]
            if i == 1:  # Special handling for beam values
                filtered_beam = filter(bool, value)
                sorted_beam = sorted(filtered_beam, key=int)
                value = ",".join(sorted_beam)
            elif i == 2:
                value = str(value)

            # Ensure that the selected_rows exist in the DataFrame
            if all(row in df.index for row in selected_rows):
                df.loc[selected_rows, column] = value
            else:
                print(f"Selected rows not found in DataFrame: {selected_rows}")

    print("After update:")
    print(df)
    return df


def create_new_row(state_values, table_column):
    new_row = {key: None for key in table_column}
    for i, column in enumerate(table_column):
        if state_values[i] is not None:
            value = state_values[i]
            # Special handling for specific columns
            if i == 1:
                value = '.'.join(value)
            if i == 3:
                filtered_beam = filter(bool, value)
                sorted_beam = sorted(filtered_beam, key=int)
                value = ",".join(sorted_beam)
            elif i == 4:
                value = f'[{value}]'
            new_row[column] = value
    return new_row


def df_runfile(filename):
    data = []
    content = ''
    if os.path.exists(filename):
        logger.info(f'{filename} exists')
        try:
            with open(filename) as file:
                content = file.read()
                file.seek(0)
                for line in file:
                    commands = line.strip().split()
                    row = {}
                    for command in commands:
                        if isinstance(command, str) and "=" in command:
                            key, value = command.split('=', 1)

                            row[key] = value
                    if row:
                        data.append(row)

            df = pd.DataFrame(data)
            df = df.rename(columns={'obsnum': 'obsnum(s)', 'obsnums': 'obsnum(s)', 'pix_list': 'exclude_beams'})
            df = df.where(pd.notna(df), None)
            if 'exclude_beams' in df.columns:
                df['exclude_beams'] = df['exclude_beams'].apply(lambda x: exclude_beams(x))
            return df, content
        except Exception as e:
            logger.error(e)
            return pd.DataFrame(), content
    else:
        logger.warning(f'{filename} does not exist')
        return pd.DataFrame(), ''


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
                    if ',' in value:
                        column = 'obsnums'
                    else:
                        column = 'obsnum'
                if column == 'exclude_beams':
                    column = 'pix_list'
                    value = exclude_beams(value)
                line += f" {column}{separator}{value}"
        lines.append(line)
    with open(runfile_path, 'w') as f:
        f.write('\n'.join(lines))


def exclude_beams(pix_list):
    if pix_list:
        beams = pix_list.split(',')
        all_strings = [str(i) for i in range(16)]
        exclude_beams = [s for s in all_strings if s not in beams]
        return ','.join(exclude_beams)
    else:
        return pix_list


def table_layout(table_data):
    output = table_data
    output[1] = table_data[1].split(',')
    # 1,2,3 to ['1', '2', '3']
    if output[3]:
        output[3] = table_data[3].split(',')
    if output[4]:
        output[4] = ast.literal_eval(output[4])

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

    return output


def create_modal(header_label, body_elements, footer_elements, modal_id):
    return dbc.Modal(
        [
            dbc.ModalHeader(dbc.Label(header_label, className='custom-bold')),
            dbc.ModalBody(body_elements),
            dbc.ModalFooter(footer_elements)
        ], id=modal_id, size='lg', centered=True, backdrop='static', scrollable=True
    )


def verify_row(new_row):
    print('new_row', new_row)


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


# check if job is running on unity
def check_job(runfile):
    return False


def make_summary(runfile):
    return True


# def get_runfile_status(current_runfile):
#     if current_runfile:
#         if os.path.exists(current_runfile):
#             message = runs.verify(current_runfile, debug=False)
#             if message:
#                 return f'Failed to Verify.' + message
#             elif check_job(current_runfile):
#                 return 'Job Running ...'
#             elif make_summary(current_runfile):
#                 return ''
#             else:
#                 return 'Verified waiting for submission'
#         else:
#             return 'Missing'
#     else:
#         return 'Not Started'


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


def make_progress_graph(progress, total):
    progress_graph = (
        go.Figure(data=[go.Bar(x=[progress])])
        .update_xaxes(range=[0, total])
        .update_yaxes(
            showticklabels=False,
        )
        .update_layout(height=100, margin=dict(t=20, b=40))
    )
    return progress_graph


def run_job_background(runfile):
    job_thread = threading.Thread(target=submit_job, args=(runfile,))
    job_thread.start()


def submit_job(runfile):
    runfile_path = os.path.dirname(runfile)
    result = subprocess.run([script_path, runfile], capture_output=True, text=True, cwd=runfile_path)

    if result.returncode == 0:
        return result.stdout
    else:
        return result.stderr

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
