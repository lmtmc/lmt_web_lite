import subprocess
import paramiko
import dash

from io import StringIO
import pandas as pd

from dash import dcc, html, Input, Output, dash_table, State
import dash_bootstrap_components as dbc
from config import config
prefix = config['path']['prefix']

# from my_server import app

#from config import config

#user = config['connect']['user']

ssh_config_file = '/home/lmt/.ssh/config'
ssh_alias = 'unity-help'
user = 'lmthelpdesk'  # Ensure this is the correct user for your squeue command


def establish_ssh_connection(ssh_config_file, ssh_alias):
    ssh_config = paramiko.SSHConfig()
    with open(ssh_config_file) as f:
        ssh_config.parse(f)

    cfg = ssh_config.lookup(ssh_alias)
    hostname = cfg['hostname']
    username = cfg['user']
    key_path = cfg['identityfile'][0]

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    private_key = paramiko.RSAKey.from_private_key_file(key_path)

    try:
        ssh.connect(hostname, username=username, pkey=private_key)
        print("SSH connection successful.")
        return ssh
    except paramiko.SSHException as e:
        print(f"SSH connection failed: {str(e)}")
        return None
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None


def execute_remote_command(ssh, command):
    try:
        stdin, stdout, stderr = ssh.exec_command(command)
        output = stdout.read().decode('utf-8').strip()
        error = stderr.read().decode('utf-8').strip()

        if error:
            print(f"Error executing command '{command}': {error}")
        return output
    except Exception as e:
        print(f"An error occurred while executing the command: {str(e)}")
        return None


def get_job_info(ssh, user):
    command = f'squeue -u {user}'
    output = execute_remote_command(ssh, command)

    if not output:
        print("No jobs found.")
        return pd.DataFrame()

    lines = output.split('\n')[1:]  # Skip the header line
    jobs = []
    columns = ['JOBID', 'PARTITION', 'NAME', 'USER', 'ST', 'TIME', 'NODES', 'NODELIST(REASON)']

    for line in lines:
        data = line.split()
        job = dict(zip(columns, data))
        jobs.append(job)

    df = pd.DataFrame(jobs)
    return df

def get_job_status(ssh, job_id):
    command_running = f'squeue -j {job_id}'
    running_jobs = execute_remote_command(ssh, command_running)
    if running_jobs:
        return f'Job {job_id} is current RUNNING'
    command_finished = f'sacct -j {job_id}'
    finished_jobs = execute_remote_command(ssh, command_finished)
    if finished_jobs:
        return f'Job {job_id} is FINISHED'
    return f'Job {job_id} is not found'

def cancel_job(ssh, job_id):
    command = f'scancel {job_id}'
    execute_remote_command(ssh, command)
    print(f"Job {job_id} cancellation requested.")



app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
layout = html.Div([
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
])

@app.callback(
    Output('job-table-unity', 'data'),
    Output('job-status', 'children'),
    Input('interval-component_unity', 'n_intervals')
)
def update_table(n):
    ssh = establish_ssh_connection('/home/lmt/.ssh/config', 'unity-help')
    if ssh:
        job_info_df = get_job_info(ssh, 'lmthelpdesk_umass_edu')
        print(job_info_df)
        if not job_info_df.empty:
            return job_info_df.to_dict('records'), 'Job list'
        ssh.close()
        print("SSH connection closed.")
    return [], 'No job'