from dash import dcc, html, Input, Output, State
from config import config
import os
import dash_bootstrap_components as dbc
from server import app, User
from flask_login import login_user
from werkzeug.security import check_password_hash


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


# lmtoy_pid_path = config['path']['work_lmt']
work_lmt = os.environ.get('WORK_LMT')

if work_lmt:
    lmtoy_pid_path = work_lmt + '/lmtoy_run'
    print('Environment variable LMT_WORK exists')
else:
    lmtoy_pid_path = config['path']['work_lmt']
    print('Environment variable LMT_WORK not exists, get it from config.txt')
# lmtoy_run path which includes the PIDs
pid_options = get_pid_option(lmtoy_pid_path)

layout = html.Div(
    children=[
        html.Div(
            # className="container",

            children=[
                dcc.Location(id='url_login', refresh=True),
                html.Div(
                    # method='Post',
                    children=[
                        dbc.Row([
                            dbc.Col([
                                html.Div('''Select a PID:''', id='h1'),
                                dcc.Dropdown(id='pid', options=pid_options)]),

                            dbc.Col([
                                html.Div('''Password:''', id='h1'),
                                dcc.Input(id='pwd-box', n_submit=0, type='password'), ]
                            ),
                        ]),

                        html.Br(),
                        html.Button(
                            children='Login',
                            n_clicks=0,
                            type='submit',
                            id='login-button'
                        ),

                        html.Div(children='', id='output-state')
                    ]
                ),
            ]
        )
    ]
)


# if the input password matches the pid password, login to that pid
@app.callback(Output('url_login', 'pathname'),
              Output('output-state', 'children'),
              [
                  Input('pid', 'value'),
                  Input('login-button', 'n_clicks'),
              ],
              State('pwd-box', 'value'),
              State('pid', 'value'),
              prevent_initial_call=True
              )
def success(pid, n_clicks,  input1, pid_state):
    print('pid', pid)

    user = User.query.filter_by(username=pid).first()
    print('user exists', user)
    if user:
        if input1:
            if check_password_hash(user.password, input1):
                if n_clicks:
                    login_user(user)
                    return '/success', ''
                else:
                    return '/login', 'Please click LOGIN button'
            else:
                return '/login', 'Incorrect password'
    else:
        return '/login', 'Please select a valid PID'


