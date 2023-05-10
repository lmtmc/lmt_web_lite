# Dash configuration
from dash import dcc, html, Input, Output, State, ALL, MATCH, dash_table
import dash_bootstrap_components as dbc
from server import app
import subprocess
import pandas as pd
import os
from config import config
from views import joblist_ssh, joblist_unity
from flask_login import current_user
# lmtoy_run path which includes the PIDs
#lmtoy_work_path = config['path']['work_lmt']
work_lmt = os.environ.get('WORK_LMT')
if work_lmt:
    lmtoy_pid_path = work_lmt + '/lmtoy_run'
    print('Environment variable LMT_WORK exists')
else:
    lmtoy_pid_path = config['path']['work_lmt']
    print('Environment variable LMT_WORK not exists, get it from config.txt')

# select PID then get the session number
PIS_options = []


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
        html.Div(html.Button(id='make-runs', children='make runs', n_clicks=0)),
        html.Br(),
        html.Div('Choose a runfile: '),
        html.Div(
            dbc.Row([
                dbc.Col(dcc.Dropdown(id='runfile', ), width=9),
                dbc.Col(html.Button('Run', id='run-btn', n_clicks=0), )
            ])
        ),

        html.Br(),
        html.Div(id='table-container'),
        html.Br(),
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

job_display_layout = html.Div([
    html.Div([
        dbc.Tabs([
            # dbc.Tab(joblist_ssh.layout, label='Run via SSH', className='content'),
            dbc.Tab(joblist_unity.layout, label='Run via Unity', className='content')
        ])
    ], className='content-container')

], className='container-width', )

# Create success layout
layout = html.Div(children=[
    dcc.Location(id='url_login_success', refresh=True),
    choose_pid_layout,
    job_display_layout,
    dcc.Store(id='store')
])


# get the runfile based on a PID and run python3 mk_runs.py
@app.callback(
    Output('runfile', 'options'),
    Input('make-runs', 'n_clicks')
)
def get_runfile(n):
    options = []
    if current_user.is_authenticated:
        path = lmtoy_pid_path + '/lmtoy_' + current_user.username
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
    Input('runfile', 'value'),
    Input('run-btn', 'n_clicks'),
    prevent_initial_call=True
)
def edit_table(runfile, n):
    if current_user.is_authenticated:
        cmd_table = dash_table.DataTable(columns=[], data=[])
        if runfile is not None:
            pid_path = lmtoy_pid_path + '/lmtoy_' + current_user.username
            runfile_path = pid_path + '/' + runfile
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
                subprocess.run('sbatch_lmtoy.sh ' + runfile, cwd=pid_path, shell=True)
        return cmd_table
