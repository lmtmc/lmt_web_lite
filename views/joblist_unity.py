import subprocess

from io import StringIO
import pandas as pd

from dash import dcc, html, Input, Output, dash_table
import dash_bootstrap_components as dbc
from server import app

from config import config

user = config['connect']['user']

def view_jobs(user):
    df = []
    try:
        squeue_output = subprocess.run(['squeue', '-u', user], capture_output=True, text=True)
        if squeue_output:
            df = pd.read_csv(StringIO(squeue_output.stdout), header=None)
            df = df.head(5)
    except:
        print('No job')


    return df


df = view_jobs(user)

data_table = dash_table.DataTable(
    id='job-table-unity',
    # columns=[{'name': i, 'id': i} for i in df.columns],
    # data=[df.to_dict('records')]
)
data_table.style_table = {
    'overflowY': 'scroll',
    'maxHeight': '200px'
}

# Create app layout
layout = html.Div(children=[
    dcc.Location(id='url_unity_df', refresh=True),
    html.Div(
        # className="container",
        children=[
            html.Div(
                html.Div(
                    # className="row",
                    children=[
                        html.Div(
                            # className="ten columns",
                            children=[
                                html.Br(),
                                html.H4('Job List if running on unity'),
                                dcc.Interval(
                                    id='interval-component_unity',
                                    interval=60 * 1000,
                                    n_intervals=0
                                ),
                                data_table

                            ]
                        ),
                    ]
                )
            )
        ]
    )
])


@app.callback(
    [
        Output('job-table-unity', 'data'),
    ],
    Input('interval-component_unity', 'n_intervals')
)
def update_job(n):
    data = []
    df = view_jobs(user)
    if df.empty:
        pass
    else:
        data = df.to_dict('records')
    return [data]
