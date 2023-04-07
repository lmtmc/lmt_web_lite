from dash import dcc, html, Input, Output, dash_table
import dash_bootstrap_components as dbc
from server import app

from fabric import Connection
# from fabric.exceptions import ConnectTimeout, AuthenticationException, SSHException, socket

from io import StringIO
import pandas as pd

from dash import dash_table

from config import config

user = config['connect']['user']
host = config['connect']['host']


def connect_to_server(host, user):
    df = pd.DataFrame()
    try:
        conn = Connection(host, user)
        print('Unity connected')
        result = conn.run(f'squeue -u {user}', hide=True)

        squeue_output = result.stdout
        df = pd.read_csv(StringIO(squeue_output), header=None)
        df = df.head(5)
        conn.close()

    except:
        print('SSH connection failed')

    return df


df = connect_to_server(host, user)

data_table = dash_table.DataTable(
    id='job-table-ssh',
    # columns=[{'name': i, 'id': i} for i in df.columns],
    # data=[df.to_dict('records')]
)
data_table.style_table = {
    'overflowY': 'scroll',
    'maxHeight': '200px'
}

# Create app layout
layout = html.Div(children=[
    dcc.Location(id='url_ssh_df', refresh=True),
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
                                html.H4('Job List via ssh'),
                                dcc.Interval(
                                    id='interval-component_ssh',
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
        Output('job-table-ssh', 'data'),
    ],
    Input('interval-component_ssh', 'n_intervals')
)
def update_job(n):
    data = []
    df = connect_to_server(host, user)
    if df.empty:
        pass
    else:
        data = df.to_dict('records')
    return [data]
