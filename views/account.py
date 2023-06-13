from dash import dcc, html, Input, Output, State, ALL, MATCH, dash_table, ctx, no_update
import dash_ag_grid as dag
import dash_bootstrap_components as dbc
from server import app, Job, db
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

layout = html.Div([
    dcc.Location(id='url_account', refresh=True),
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader('Job History'),
                dbc.CardBody(html.Div(id='job-history')),
                dbc.CardFooter(html.Button('create a new job', id='new-job'))
            ],className='h-100')
        ], width=7),
        dbc.Col(
            [
                dbc.Card([
                    dbc.CardHeader('Job Details'),
                    dbc.CardBody(
                        [
                            html.Div(id='job-title'),
                            html.Pre(id='job-content'),
                        ]
                    )
                        # html.Button('Edit', id='job-edit-btn', style={'display': 'none'})
                    ], className='h-100'),
                ], width=5
        )
    ])
])

linked_source = []


#
@app.callback(
    Output('job-history', 'children'),
    [Input('url', 'pathname')]
)
def display_job_history(n):
    # get current user's jobs and put it in a pandas df
    data = {
        'ID': [],
        'Title': [],
        'Submitted Time': [],
        'Session': [],
        'Status': [],
        # 'Edit': [],
        'Result': []
    }
    linked_source = []
    if current_user:
        jobs = Job.query.filter_by(username=current_user.username).all()
        for job in jobs:
            data['ID'].append(job.id)
            data['Submitted Time'].append(job.create_time)
            data['Title'].append(job.title)
            data['Session'].append(job.session)
            data['Status'].append('Status')
            # data['Edit'].append('Edit')
            data['Result'].append('Result')
        print('data', data)
    df = pd.DataFrame(data)
    for x in df.Result:
        linked_source.append(f'[{x}](https://www.{x}.com)')
    df.Result = linked_source
    print('df', df)

    job_history_grid = dag.AgGrid(
        id='job-table',
        rowData=df.to_dict('records'),
        # columnDefs=[{'field': col, 'flex': flex} for col, flex in zip(df.columns, flex_width)],
        columnDefs=[
            {'field': 'ID', 'flex': 1},
            {'field': 'Title', 'flex': 3, "checkboxSelection": True},
            {'field': 'Submitted Time', 'flex': 2},
            {'field': 'Session', 'flex': 1, },
            {'field': 'Status', 'flex': 1},
            {'field': 'Result', 'flex': 2, 'cellRenderer': 'markdown'}
        ],
        defaultColDef={"resizable": True, "sortable": True, "filter": True, "minWidth": 125},
        # columnSize="sizeToFit",
        dashGridOptions={"rowSelection": "single"},
        style={'height': 600, "margin": 20, }
    )

    return job_history_grid


@app.callback(
    Output('job-title', 'children'),
    Output('job-content', 'children'),
    # Output('job-edit-btn', 'style'),
    Input('job-table', 'selectedRows')
)
def show_job_detail(selected):
    if selected:
        job = selected[0]
        job_title = job['Title']
        print('job is', job)
        pid_path = lmtoy_pid_path + '/lmtoy_' + current_user.username
        runfile_path = pid_path + '/' + job['Session'] + '/lmtoy_run/lmtoy_' + current_user.username + '/' + job[
            'Title']
        with open(runfile_path, 'r') as file:
            job_content = file.read()
        return f'Job_detail for {job_title}', f'{job_content}'
    return 'Select a job to view details', ''


@app.callback(
    Output('url_account', 'pathname'),
    Input('new-job', 'n_clicks'),
    State('url_account', 'pathname'),
    prevent_initial_call=True
)
def create_job(n, pathname):
    if n:
        return '/session'
    else:
        return pathname
