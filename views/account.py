from dash import dcc, html, Input, Output, State, ctx, no_update
import dash_ag_grid as dag
import dash_bootstrap_components as dbc
from my_server import app, Job
import pandas as pd
import os
from config import config
from flask_login import current_user

user = 'lmthelpdesk_umass_edu'
work_lmt = os.environ.get('WORK_LMT')
if work_lmt:
    lmtoy_pid_path = work_lmt + '/lmtoy_run'
    print('account: WORK_LMT =',work_lmt)
else:
    lmtoy_pid_path = config['path']['work_lmt']
    print('Environment variable WORK_LMT not exists, get it from config.txt')

job_list = dbc.Card(
    [
        dbc.CardHeader(
            dbc.Row(
                [
                    dbc.Col(dbc.Label('Job History', className='custom-bold'), width='auto'),
                    dbc.Col(
                        html.Button(
                            [html.I(className="fas fa-plus me-2"), 'New Job'],
                            id='new-job',
                            className='ms-auto'
                        ), width='auto', style={'margin-left': 'auto'}
                    ),
                ], justify='between', align='center'
            )
        ),
        dbc.CardBody(html.Div(id='job-history'))
    ]
)
job_table = html.Div(dag.AgGrid(id='job-table'), style={'display': 'none'})

job_modal = dbc.Modal(
    [
        dbc.ModalHeader(dbc.Label(id='job-title', className='custom-bold')),
        dbc.ModalBody(html.Pre(id='job-content'), ),
        dbc.ModalFooter(html.Button("Close", id="job-content-close", className="ml-auto"))
    ],
    id='job-content-modal', size='lg', centered=True
)

layout = html.Div([dcc.Location(id='url_account', refresh=True),
                   job_list,
                   job_modal,
                   job_table
                   ])


@app.callback(
    Output('job-history', 'children'),
    [Input('url_account', 'pathname')]
)
def display_job_history(n):
    # get current user's jobs and put it in a pandas df
    data = {
        'ID': [],
        'Title': [],
        'Submitted Time': [],
        'Session': [],
        'Status': [],
        'Result': []
    }
    linked_source = []
    if current_user.is_authenticated:
        jobs = Job.query.filter_by(username=current_user.username).all()
        for job in jobs:
            data['ID'].append(job.id)
            data['Submitted Time'].append(job.create_time)
            data['Title'].append(job.title)
            data['Session'].append(job.session)
            # todo replace 'Status' and 'Result'
            data['Status'].append('Status')
            data['Result'].append('Result')
    df = pd.DataFrame(data)
    linked_source = [f'[{x}](https://www.{x}.com)' for x in df.Result]
    df.Result = linked_source

    job_history_grid = dag.AgGrid(
        id='job-table',
        rowData=df.to_dict('records'),
        columnDefs=[
            {'field': 'ID', 'flex': 1},
            {'field': 'Title', 'flex': 3, 'cellRenderer': 'DBC_Button',
             "cellRendererParams": {"className": "link-button"}},
            {'field': 'Submitted Time', 'flex': 2},
            {'field': 'Session', 'flex': 1, },
            {'field': 'Status', 'flex': 1},
            {'field': 'Result', 'flex': 2, 'cellRenderer': 'markdown'}
        ],
        defaultColDef={"resizable": True, "sortable": True, "filter": True, "minWidth": 125},
        dashGridOptions={"rowSelection": "single",
                         "enableCellTextSelection": True,
                         "ensureDomOrder": True,
                         "pagination": True, "paginationAutoPageSize": True},
        style={'height': 500, "margin": 20, }
    )

    return job_history_grid


@app.callback(
    Output('job-title', 'children'),
    Output('job-content', 'children'),
    Output('job-content-modal', 'is_open'),
    [
        Input('job-table', 'cellClicked'),
        Input('job-table', 'selectedRows'),
        Input('job-content-close', 'n_clicks')],
    prevent_initial_call=True
)
def show_job_detail(selected_cell, selected_row, n):
    if ctx.triggered_id == 'job-content-close' or not selected_cell:
        return no_update, no_update, False

    if selected_cell['value'] == selected_row[0]['Title']:
        job_title = selected_cell['value']
        session = selected_row[0]['Session']
        pid_path = lmtoy_pid_path + '/lmtoy_' + current_user.username
        runfile_path = pid_path + '/' + session + '/lmtoy_run/lmtoy_' + current_user.username + \
                       '/' + job_title
        try:
            with open(runfile_path, 'r') as file:
                job_content = file.read()
        except FileNotFoundError:
            return f"Job content for {job_title} not found", "The specified job content file does not exist", True
        return f'Job content for {job_title}', f'{job_content}', True
    return no_update, no_update, False


@app.callback(
    Output('url_account', 'pathname'),
    Input('new-job', 'n_clicks'),
    State('url_account', 'pathname'),
    prevent_initial_call=True
)
def create_job(n, pathname):
    if n:
        return '/project'
    return pathname
