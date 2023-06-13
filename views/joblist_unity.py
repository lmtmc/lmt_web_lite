import subprocess

from io import StringIO
import pandas as pd

from dash import dcc, html, Input, Output, dash_table, State
import dash_bootstrap_components as dbc
from my_server import app

from config import config

user = config['connect']['user']


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


def view_jobs(user):
    df = pd.DataFrame()
    try:
        squeue_output = subprocess.run(['squeue', '-u', user], capture_output=True, text=True)
        if squeue_output:
            df = pd.read_csv(StringIO(squeue_output.stdout), header=None)
            df = df.head(5)
    except:
        print('No job')

    return df


df = view_jobs(user)

layout = dbc.Card(
    [
        dbc.CardHeader('Jobs running on unity'),
        dbc.CardBody(
            [
                html.Div(id='job-status'),
                dcc.Interval(
                    id='interval-component_unity',
                    interval=10 * 1000,
                    n_intervals=0),
                dash_table.DataTable(
                    id='job-table-unity',
                    data=[],
                    columns=
                    [{'name': 'JOBID', 'id': 'JOBID'},
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
            ]),

        dbc.CardFooter([
            html.Button('Cancel selected job', id='cancel-button'),
            html.Div(id='cancel-status')
        ])],
    style={'height': '800px'}
    # className='content-container'
)


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
