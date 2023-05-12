# Dash configuration
from dash import dcc, html, Input, Output, State, ALL, MATCH, dash_table, ctx
import dash_bootstrap_components as dbc
from server import app
import subprocess
import pandas as pd
import os
from config import config
from flask_login import current_user
from io import StringIO

# lmtoy_run path which includes the PIDs
# lmtoy_work_path = config['path']['work_lmt']
user = 'lmthelpdesk_umass_edu'
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
    df = pd.DataFrame()
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


# save revised data to a runfile
def save_runfile(df, runfile_path):
    separator = '='
    lines = []
    for row in df.to_dict('records'):
        line = 'SLpipeline.sh'
        for column, value in row.items():
            line += f" {column}{separator}{value}"
        lines.append(line)
    print('runfile_path', runfile_path)
    with open(runfile_path, 'w') as f:
        f.write('\n'.join(lines))


def view_jobs(user):
    df = pd.DataFrame()
    try:
        squeue_output = subprocess.run(['squeue', '-u', user], capture_output=True, text=True)
        if squeue_output:
            df = pd.read_csv(StringIO(squeue_output.stdout), header=None)
            # df = df.head(5)
    except:
        print('No job')

    return df


def get_job_info():
    result = subprocess.run(['squeue', '-u', user], stdout=subprocess.PIPE, text=True)
    output = result.stdout.strip().split('\n')[1:]
    jobs = []
    columns = ['JOBID', 'PARTITION', 'NAME', 'USER', 'ST', 'TIME', 'NODES', 'NODELIST(REASON)']
    for line in output:
        data = line.split()
        job = {}
        for i in range(len(columns)):
            job[columns[i]] = data[i]
        jobs.append(job)
    df = pd.DataFrame(jobs)
    return df


def cancel_job(job_id):
    subprocess.run(['scancel', job_id])


choose_pid_layout = html.Div(
    className="container",
    children=[
        html.Div(html.Button(id='make-runs', children='make runs', n_clicks=0)),
        html.Br(),
        html.Div('Choose a runfile: '),
        html.Div(dcc.Dropdown(id='runfile', )),

        html.Br(),
        dash_table.DataTable(
            id='table',
            editable=True,
            data=[],
            row_deletable=True,
            row_selectable='multi',

        ),
        html.Br(),
        # todo filename should be validated before saving
        html.Div([dbc.Row([
            dbc.Col(html.Button('Add a row', id='add-row-btn')),
            dbc.Col(html.Button('Add a column', id='add-col-btn')),
        ]),
            html.Br(),
            dbc.Row([
                dbc.Col(dcc.Input(id='filename-input', type='text', placeholder='Enter filename')),
                dbc.Col(html.Button('Save', id='save-btn')),
                dbc.Col(html.Button('Run', id='run-btn', n_clicks=0, style={'background-color': 'orange'}), )
            ]),

        ], id='save-table', style={'display': 'none'}),
        html.Br(),
        html.Div(id='save-state'),
        html.Br(),

    ])

job_display_layout = html.Div([
    html.H5('Jobs running on unity'),
    html.Div(id='job-status'),
    dcc.Interval(
        id='interval-component_unity',
        interval=10 * 1000,
        n_intervals=0
    ),
    dash_table.DataTable(
        id='job-table-unity',
        data=[],
        columns=[{'name': 'JOBID', 'id': 'JOBID'},
                 {'name': 'PARTITION', 'id': 'PARTITION'},
                 {'name': 'NAME', 'id': 'NAME'},
                 {'name': 'USER', 'id': 'USER'},
                 {'name': 'ST', 'id': 'ST'},
                 {'name': 'TIME', 'id': 'TIME'},
                 {'name': 'NODES', 'id': 'NODES'},
                 {'name': 'NODELIST(REASON)', 'id': 'NODELIST(REASON)'}],
        row_selectable='single',
        style_table={'overflowX': 'scroll'}
    ),
    html.Br(),
    html.Button('Cancel selected job', id='cancel-button'),
    html.Div(id='cancel-status')
], className='content-container')

run_files_layout = html.Div(
    className='container',
    children=[
        dbc.Spinner(html.Div(id='job-running-status'), color='primary', type='grow'),
        job_display_layout,
        dcc.Link('Make Summary', id='make-summary', href='https://taps.lmtgtm.org', target="_blank",
                 style={'display': 'none'}),
    ])

# Create success layout
layout = html.Div(children=[
    dcc.Location(id='url_login_success', refresh=True),
    choose_pid_layout,
    run_files_layout,
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


# todo need more validaton here
# display an editable dash table based on runfile
@app.callback(
    Output('table', 'data'),
    Output('table', 'columns'),
    Output('save-table', 'style'),
    Input('runfile', 'value'),
    Input('add-row-btn', 'n_clicks'),
    Input('add-col-btn', 'n_clicks'),
    State('table', 'data'),
    State('table', 'columns'),
    prevent_initial_call=True
)
def display_table(runfile, n1, n2, data, columns):
    if current_user.is_authenticated:
        save_file_style = {'display': 'none'}
        if runfile:
            pid_path = lmtoy_pid_path + '/lmtoy_' + current_user.username
            runfile_path = pid_path + '/' + runfile
            df = df_runfile(runfile_path)
            data = df.to_dict('records')
            columns = [{'name': col, 'id': col, 'deletable': True, 'renamable': True} for col in df.columns]
            if not df.empty:
                save_file_style = {'display': 'inline-block'}
                if ctx.triggered:
                    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
                    if button_id == 'add-row-btn':
                        data.append({col['id']: '' for col in columns})
                    if button_id == 'add-col-btn':
                        columns.append({'name': f'Column {len(columns) + 1}', 'id': f'column_{len(columns) + 1}',
                                        'deletable': True, 'renamable': True})

        return data, columns, save_file_style


@app.callback(
    Output('save-state', 'children'),
    Output('filename-input', 'value'),
    Input('save-btn', 'n_clicks'),
    State('runfile', 'value'),
    State('filename-input', 'value'),
    State('table', 'data'),
)
def save_table(n_clicks, runfile, newfile, data):
    if runfile is not None:
        pid_path = lmtoy_pid_path + '/lmtoy_' + current_user.username
        # save the data to the new file if given a newfile name, else use the old filename
        if newfile:
            runfile_path = pid_path + '/' + newfile
        else:
            runfile_path = pid_path + '/' + runfile

        df = pd.DataFrame(data)
        save_runfile(df, runfile_path)
        return f'Data saved to {runfile_path}', ''
    return '', ''


@app.callback(
    Output('job-running-status', 'children'),
    Input('run-btn', 'n_clicks'),
    State('runfile', 'value'),
)
def run_file(n, runfile):
    if runfile:
        pid_path = lmtoy_pid_path + '/lmtoy_' + current_user.username
        print('sbatch_lmtoy.sh $PID.run1')
        result = subprocess.run('sbatch_lmtoy.sh ' + runfile, cwd=pid_path, shell=True)
        print('result', result)
        return result.stdout


@app.callback(
    Output('job-table-unity', 'data'),
    Output('job-status', 'children'),
    Input('interval-component_unity', 'n_intervals')
)
def update_table(n):
    df = get_job_info()
    data = []
    if not df.empty:
        return df.to_dict('records'), 'Job list'
    return [data], 'No job'


@app.callback(
    Output('cancel-status', 'children'),
    Input('cancel-button', 'n_clicks'),
    State('job-table-unity', 'selected_rows')
)
def cancel_slurm_job(n, selected_rows):
    if n:
        job_id = get_job_info().iloc[selected_rows[0]]['JOBID']
        print('job_id to cancel', job_id)
        cancel_job(job_id)
        return f'Cancel job {job_id}.'
    else:
        return ''


@app.callback(
    Output('make-summary', 'style'),
    Output('make-summary', 'href'),
    Input('interval-component_unity', 'n_intervals'),
)
def make_summary(n):
    if get_job_info().empty:
        return {'display': 'inline-block'}, 'https://taps.lmtgtm.org/lmtslr/2023-S1-US-18/Session-1/2023-S1-US-18/'
    else:
        return {'display': 'none'}, 'https://taps.lmtgtm.org'
# # todo make the job cancelable
# @app.callback(
#     Output('job-table-unity', 'data'),
#     Output('all-done', 'children'),
#     Output('make-summary', 'style'),
#     Output('make-summary', 'href'),
#     Input('interval-component_unity', 'n_intervals'),
#     prevent_initial_call=True
# )
# def update_job(n):
#     data = []
#     make_summary_style = {'display': 'none'}
#     url = 'https://taps.lmtgtm.org/'
#
#     jobs = get_job_info()
#     jobs_with_buttons = []
#     for job in jobs:
#         job_id = job[0]
#         cancel_button = html.Button('Cancel', id=f'cancel-button-{job_id}')
#         cancel_button.callback = dash.dependencies.callback(dash.dependencies.Output('cancel-button', 'children'),
#                                                             [dash.dependencies.Input(f'cancel-button-{job_id}', 'n_clicks')])(lambda n: cancel_job(job_id))
#     url = 'https://taps.lmtgtm.org/lmtslr/2023-S1-US-18/Session-1/2023-S1-US-18/'
#     if df.empty:
#         # job is done, show the make summary button
#         make_summary_style = {'display': 'inline-block'}
#     else:
#         # job is still running, hide the make summary button
#         data = df.to_dict('records')
#     return [data], make_summary_style, url
