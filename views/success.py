# Dash configuration
from dash import dcc, html, Input, Output, State, ALL, MATCH, dash_table
import dash_bootstrap_components as dbc
from server import app
import subprocess
import pandas as pd
import os
from config import config

lmt_work_path = config['path']['work_lmt']
# lmtoy_run path which includes the PIDs
lmtoy_pid_path = lmt_work_path + '/lmtoy_run'

# select PID then get the session number
PIS_options = []


# get the pid options in the lmtoy_pid_path
def get_pid_option(path):
    pid_options = []
    folders = [f.path for f in os.scandir(path) if f.is_dir()]
    for folder in folders:
        folder_name = os.path.basename(folder)
        if folder_name.startswith('lmtoy_'):
            folder = folder_name.split('_')[1]
            pid_options.append(os.path.basename(folder))
    return pid_options


pid_options = get_pid_option(lmtoy_pid_path)


# get the runfile options in the lmtoy_runfile_path
def get_runfile_option(path):
    files = os.listdir(path)
    runfile_options = [file for file in files if 'run' in file and not file.endswith('.py')]
    return runfile_options


# Parse the runfile into a DataFrame
def df_runfile(filename):
    data = []
    for line in open(filename):
        commands = line.strip().split()
        row = {}
        for command in commands:
            if '=' in command:
                key = command.split('=')[0]
                value = command[command.index('=') + 1:]
                row[key] = value
        data.append(row)
        df = pd.DataFrame(data)
    return df


choose_pid_layout = html.Div(
    className="container",
    children=[
        html.Div('Choose a PID: '),
        html.Div(
            dbc.Row([
                dbc.Col(dcc.Dropdown(id='pid', options=pid_options), width=9),
                dbc.Col(html.Button(id='make-runs', children='make runs', n_clicks=0)),
            ])),
        html.Br(),
        html.Div('Choose a runfile: '),
        dcc.Dropdown(id='runfile', ),
        html.Br(),
        html.Div(id='table-container'),
        html.Br(),
        html.Button('Run', id='run-btn', n_clicks=0),
        html.Div(id='output-message')

    ])

run_files_layout = html.Div(
    dbc.Modal([dbc.ModalTitle('Run file'),
               dbc.ModalBody(dbc.Spinner(color='primary', type='grow'),
                             id='run-file-output', style={'overflowY': 'auto'}),
               dbc.ModalFooter(
                   html.Button('Close', id='close', className='ml-auto')
               )], id='run-file-output', size='xl', is_open=False)
)

# Create success layout
layout = html.Div(children=[
    dcc.Location(id='url_login_success', refresh=True),
    choose_pid_layout,
    run_files_layout,
    dcc.Store(id='store')
])


# get the runfile based on a PID
@app.callback(
    Output('runfile', 'options'),
    Input('pid', 'value'),
    Input('make-runs', 'n_clicks')
)
def get_runfile(pid_value, n):
    options = []
    if pid_value is not None:
        path = lmtoy_pid_path + '/lmtoy_' + pid_value
        if n:
            # command of python3 mk_runs.py
            cmd = ['python3', path + '/mk_runs.py']
            # run the command and save the runfiles in path
            subprocess.run(cmd, cwd=path, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            options = get_runfile_option(path)
    return options


# display an editable dash table based on runfile
@app.callback(
    Output('table-container', 'children'),
    Input('pid', 'value'),
    Input('runfile', 'value'),
    Input('run-btn','n_clicks'),
    prevent_initial_call=True
)
def edit_table(pid_value, runfile, n):
    if pid_value is not None and runfile is not None:
        pid_path = lmtoy_pid_path + '/lmtoy_' + pid_value
        runfile_path = pid_path+'/'+runfile
        df = df_runfile(runfile_path)
        cmd_table = dash_table.DataTable(
            id='table',
            columns=[{'name': i, 'id': i} for i in df.columns],
            data=df.to_dict('records'),
            editable=True,
            row_deletable=True,
            row_selectable='multi'
        ),
        if n:
            
        # sbatch_lmtoy.sh $PID.run1
            subprocess.run('sbatch_lmtoy.sh '+runfile,cwd=pid_path,shell=True)
        return cmd_table

# @app.callback(
#     Output('source', 'options'),
#     Output('pis', 'options'),
#     Output('session-alert', 'children'),
#     Input('pid', 'value'),
#     Input('add-btn', 'n_clicks'),
#     State('add-session', 'value'),
#     prevent_initial_call=True
# )
# def get_options(pid_value, n, add_new):
#     pis_options = ['create a new session']
#     source_options = []
#     session_alert = dbc.Alert(is_open=False)
#     # get the folder name as session options
#     pis_path = lmtoy_run_path + '/lmtoy_' + pid_value
#     subfolders = [f.path for f in os.scandir(pis_path) if f.is_dir()]
#     for subfolder in subfolders:
#         folder_name = os.path.basename(subfolder)
#         if folder_name.startswith('session'):
#             pis_options.append(os.path.basename(subfolder))
#     # if press add button, add the input to session option
#     if n:
#         if add_new in pis_options:
#             session_alert = dbc.Alert('session name exists', color='secondary', dismissable=True)
#         else:
#             # create a session folder
#             os.makedirs(os.path.join(pis_path, add_new))
#             session_alert = dbc.Alert(f'{add_new} created', color='success', dismissable=True)
#             pis_options.append(add_new)
#
#     # get the source options (fake data for now)
#     # todo
#
#     source_file = pis_path + '/source.txt'
#     try:
#         with open(source_file, 'r') as file:
#             source_options = [line.strip() for line in file.readlines()]
#     except:
#         print('no source file in this folder')
#     return source_options, pis_options, session_alert
#
#
# @app.callback(
#     Output('session-modal', 'is_open'),
#     Input('pis', 'value'),
#     Input('close-btn', 'n_clicks'),
#     Input('add-btn', 'n_clicks'),
#     State('session-modal', 'is_open'),
#     State('add-session', 'value'),
#     State('pis', 'value')
# )
# def show_output(option, n1, n2, is_open, new_session, pis_value):
#     print('create a new session', option)
#     if option == 'create a new session':
#         is_open = True
#     if n1 or n2:
#         is_open = False

# return is_open


# @app.callback(
#     Output('run-file-output', 'children'),
#     [Input('pid', 'value'),
#      Input('pis', 'value'),
#      Input('run-file', 'is_open')],
#     prevent_initial_call=True)
# def run_file(pid, pis, is_open):
#     if is_open:
#         run_path = lmt_work_path + '/lmtoy_' + pid
#         subprocess.run('lmtoy', capture_output=True, text=True)
#         result = subprocess.run(run_path + 'make runs', capture_output=True, text=True)
#         output = result.stdout
#
#         return html.Pre(output)
#
#
# # click next to run file
# @app.callback(
#     Output('run-file', 'is_open'),
#     [Input('next-button', 'n_clicks'), Input('close', 'n_clicks')],
#     [State('run-file', 'is_open')]
# )
# def toggle_modal(n1, n2, is_open):
#     if n1 or n2:
#         return not is_open
#     return is_open
# runfile_modal = dbc.Modal(
#     [
#         dbc.Label("Edit Parameters"),
#         dbc.ModalBody(html.Div(id='runfile-table')),
#         dbc.ModalFooter(
#             html.Button(
#                 "Save", id="save-btn", className="ms-auto"),
#         ),
#
#     ],
#     id='runfile-modal',
#     is_open=False,
#     centered=True,
#     size='lg'
#
# )
# session_modal = dbc.Modal(
#     [
#         dbc.Label("Create a new session"),
#         dbc.ModalBody(
#             [dcc.Input(id='add-session'),
#              html.Button('Add', id='add-btn'),
#              ]),
#         dbc.ModalFooter(
#             html.Button(
#                 "Close", id="close-btn", className="ms-auto"),
#         ),
#
#     ],
#     id='session-modal',
#     is_open=False,
#     centered=True,
#     size='lg'
#
# )
