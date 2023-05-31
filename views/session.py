from dash import dcc, html, Input, Output, State, ALL, MATCH, dash_table, ctx, no_update
import dash_ag_grid as dag
import dash_bootstrap_components as dbc
from server import app
import subprocess
import pandas as pd
import os
import shutil
from config import config
from flask_login import current_user
import platform
from datetime import datetime
from io import StringIO

user = 'lmthelpdesk_umass_edu'
work_lmt = os.environ.get('WORK_LMT')
if work_lmt:
    lmtoy_pid_path = work_lmt + '/lmtoy_run'
    print('Environment variable LMT_WORK exists')
else:
    lmtoy_pid_path = config['path']['work_lmt']
    print('Environment variable LMT_WORK not exists, get it from config.txt')

myFmt = '%Y-%m-%d %H:%M:%S'


# get the sessions' name in the path
def get_session_names(path):
    session_names = []
    if path:
        files = os.listdir(path)
        session_names = [file for file in files if file.startswith('session')]
        session_names.sort()
    return session_names


# get the runfile options in the path
def get_runfile_option(path):
    files = os.listdir(path)
    runfile_options = [file for file in files if 'run' in file and not file.endswith('.py')]
    runfile_options.sort()
    return runfile_options


# Parse the runfile into a DataFrame
def df_runfile(filename):
    data = []
    df = pd.DataFrame()
    if os.path.exists(filename):
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


runfile_table = html.Div(
    [
        dash_table.DataTable(
            id='table',
            editable=True,
            data=[],
            row_deletable=True,
            row_selectable='multi',
            style_table={'overflowX': 'auto'}
        ),
        html.Br(),
        # todo filename should be validated before saving
        html.Div([dbc.Row([
            dbc.Col(html.Button('Add a row', id='add-row-btn')),
            dbc.Col(html.Button('Add a column', id='add-col-btn')),
        ]),
            html.Br(),

        ], id='save-table', style={'display': 'none'}),
        html.Br(),
        html.Div(id='save-state'),
        html.Br(),
    ]
)

pid_path = ''

if current_user:
    if current_user.is_authorized:
        pid_path = lmtoy_pid_path + '/lmtoy_' + current_user.username

print('pid_path', pid_path)

session_layout = html.Div(
    dbc.Card(
        [
            dbc.CardHeader(html.H6('Choose a session or create a new'), ),
            dbc.CardBody(dbc.RadioItems(id='session-select', options=get_session_names(pid_path), inline=True,
                                        style={"height": "100px", 'overflow-y': 'scroll'}), ),
            dbc.CardFooter([

                dbc.Row(
                    [
                        dbc.Col(html.Button('Delete session', id='session-del'), ),
                        dbc.Col(dcc.Input(placeholder='Session Name', id='session-name',
                                          ), ),
                        dbc.Col(html.Button('Add session', id='session-add'), ),
                    ]
                ),

                dbc.Alert(id='new-session-message', is_open=False,
                          color='secondary', dismissable=True, style={'font-size': '15px'}),

                html.Div(dcc.ConfirmDialog(
                    id='confirm-del-session',
                    message='Are you sure you want to delete?'
                ), style={'position': 'relative', "top": "100px"}),
            ])
        ],
    ),
)

runfile_layout = html.Div(
    dbc.Card(
        [
            dbc.CardHeader(html.H6('Select a session to view details', id='runfiles-label')),
            dbc.CardBody([
                dbc.RadioItems(id='runfile-select', inline=True),
                dbc.Col(html.Div(dbc.Button(id='make-runs', children='make runs',
                                            color='secondary', n_clicks=0))),
            ], style={"height": "100px", 'overflow-y': 'scroll'}),
            dbc.CardFooter([
                dbc.Row(
                    [
                        dbc.Col(html.Button('Delete runfile', id='runfile-del'), ),
                        dbc.Col(dcc.Input(placeholder='Runfile Name', id='runfile-name', ), ),
                        dbc.Col(html.Button('Add runfile', id='runfile-add'), ),
                    ]
                ),

                dbc.Alert(id='new-runfile-message', is_open=False,
                          color='secondary', dismissable=True, style={'font-size': '15px'}),

                html.Div(dcc.ConfirmDialog(
                    id='confirm-del-runfile', message='Are you sure you want to delete?'),
                    style={'position': 'relative', "top": "100px"})
            ]

            )]
    ), )

parameter_layout = html.Div(
    dbc.Card([
        dbc.CardHeader(html.H6('Runfile content:', id='runfile-content')),
        dbc.CardBody(runfile_table,
                     style={"height": "200px", "overflowY": "scroll"}),
        dbc.CardFooter(
            dbc.Row([
                dbc.Col(dcc.Input(id='filename-input', type='text',
                                  placeholder='New Runfile Name')),
                dbc.Col(html.Button('Save', id='save-btn')),
                dbc.Col(html.Button('Run', id='run-btn', n_clicks=0,
                                    style={'background-color': 'orange'}), )
            ])
        )

    ], ))

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

layout = html.Div(
    [
        session_layout,
        html.Br(),
        runfile_layout,
        html.Br(),
        parameter_layout,
        html.Br(),
        job_display_layout

    ]
)


# show the existing session and add session button
@app.callback(Output('new-session-message', 'children'),
              Output('new-session-message', 'is_open'),
              Output('session-select', 'options'),
              Output('session-select', 'value'),
              Output('session-name', 'value'),
              Input('session-select', 'value'),
              Input('confirm-del-session', 'submit_n_clicks'),
              Input('session-add', 'n_clicks'),
              State('session-name', 'value'), )
def session_display(session, n1, n2, name):
    pid_path = ''
    session_value = session
    if current_user:
        if current_user.is_authenticated:
            pid_path = lmtoy_pid_path + '/lmtoy_' + current_user.username
    names = get_session_names(pid_path)
    print('session names', names)
    message = ''
    is_open = False
    if ctx.triggered:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        # todo add a 'are you sure to delete' to double check
        if button_id == 'confirm-del-session':
            is_open = True
            if session:
                try:
                    shutil.rmtree(os.path.join(pid_path, session))
                    message = f'{session} deleted!'
                    session_value = None
                except Exception as e:
                    print(f'Error creating folder: {str(e)}')
        if button_id == 'session-add':
            is_open = True
            print('name', name)
            if name:
                if name not in names:
                    try:
                        os.mkdir(os.path.join(pid_path, name))
                        message = f'{name} created!'
                        session_value = name
                    except Exception as e:
                        print(f'Error creating folder: {str(e)}')
                else:
                    message = f"{name} exists"
            else:
                message = 'Please input a session name!'
                print('message', message)
    names = get_session_names(pid_path)
    print('names', names)
    return message, is_open, names, session_value, ''


# if click delete button show the confirmation
@app.callback(
    Output('confirm-del-session', 'displayed'),
    Input('session-del', 'n_clicks'),
    prevent_initial_call=True
)
def display_confirmation(n_clicks):
    if n_clicks:
        return True


# show runfiles in selected session
@app.callback(Output('new-runfile-message', 'children'),
              Output('new-runfile-message', 'is_open'),
              Output('runfile-select', 'options'),
              Output('runfile-select', 'value'),
              Output('runfile-name', 'value'),
              Input('session-select', 'value'),
              Input('runfile-select', 'value'),
              Input('confirm-del-runfile', 'submit_n_clicks'),
              Input('runfile-add', 'n_clicks'),
              Input('make-runs', 'n_clicks'),
              State('runfile-name', 'value'),
              prevent_initial_call=True)
def runfile_display(session, runfile, n1, n2, n3, name):
    session_path = ''
    runfile_value = runfile
    names = []
    is_open = False
    message = ''
    if current_user:
        if current_user.is_authenticated:
            if session:
                pid_path = lmtoy_pid_path + '/lmtoy_' + current_user.username
                session_path = pid_path + '/' + session
                names = get_runfile_option(session_path)
                print('runfile names', names)
                if ctx.triggered:
                    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
                    if button_id == 'confirm-del-runfile':
                        is_open = True
                        if runfile:
                            try:
                                print('file to be removed', session_path + '/' + runfile)
                                os.remove(session_path + '/' + runfile)
                                message = f'{runfile} deleted!'
                                runfile_value = None
                            except Exception as e:
                                print(f'Error creating folder: {str(e)}')
                    if button_id == 'runfile-add':
                        is_open = True
                        if name:
                            if name not in names:
                                try:
                                    with open(session_path + '/' + name, 'x') as file:
                                        # todo create a empty runfile
                                        pass
                                    message = f'{name} created!'
                                    runfile_value = name
                                except Exception as e:
                                    print(f'Error creating folder: {str(e)}')
                            else:
                                message = f"{name} exists"
                        else:
                            message = 'Please input a runfile name!'
                    if button_id == 'make-runs':
                        print('move make runs')
                        cmd1 = ['cp', 'mk_runs.py', session_path]
                        subprocess.run(cmd1, cwd=pid_path, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                        cmd2 = ['python3', session_path + '/mk_runs.py']
                        # run the command and save the runfiles in path
                        subprocess.run(cmd2, cwd=session_path, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    names = get_runfile_option(session_path)
    return message, is_open, names, runfile_value, ''


# if click delete runfile button show the confirmation
@app.callback(
    Output('confirm-del-runfile', 'displayed'),
    Input('runfile-del', 'n_clicks'),
    prevent_initial_call=True
)
def runfile_display_confirmation(n_clicks):
    if n_clicks:
        return True


# todo need more validation here
# display an editable dash table based on runfile
@app.callback(
    Output('table', 'data'),
    Output('table', 'columns'),
    Output('save-table', 'style'),
    Input('runfile-select', 'value'),
    Input('session-select', 'value'),
    Input('add-row-btn', 'n_clicks'),
    Input('add-col-btn', 'n_clicks'),
    State('table', 'data'),
    State('table', 'columns'),
    prevent_initial_call=True)
def display_runfile_table(runfile, session, n1, n2, data, columns):
    save_file_style = {'display': 'none'}

    # if runfile exists
    if runfile:
        pid_path = lmtoy_pid_path + '/lmtoy_' + current_user.username
        runfile_path = pid_path + '/' + session + '/' + runfile
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
    Input('session-select', 'value'),
    State('runfile-select', 'value'),
    State('filename-input', 'value'),
    State('table', 'data'),
)
def save_table(n_clicks, session, runfile, newfile, data):
    if ctx.triggered:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        if button_id == 'save-btn':
            if runfile:
                pid_path = lmtoy_pid_path + '/lmtoy_' + current_user.username
                session_path = pid_path + '/' + session
                # save the data to the new file if given a newfile name, else use the old filename
                if newfile:
                    runfile_path = session_path + '/' + newfile
                else:
                    runfile_path = session_path + '/' + runfile

                df = pd.DataFrame(data)
                save_runfile(df, runfile_path)
            return f'Data saved to {runfile_path}', ''
    return '', ''


@app.callback(
    Output('job-running-status', 'children'),
    Input('run-btn', 'n_clicks'),
    State('session-select', 'value'),
    State('runfile-select', 'value'),
)
def run_file(n, session, runfile):
    if runfile:
        session_path = lmtoy_pid_path + '/lmtoy_' + current_user.username + '/' + session
        print('sbatch_lmtoy.sh $PID.run1')
        result = subprocess.run('sbatch_lmtoy.sh ' + runfile, cwd=session_path, shell=True)
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
