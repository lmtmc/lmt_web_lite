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


lmtoy_pid_path = config['path']['work_lmt']
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
                  Input('pwd-box', 'n_submit'),
              ],
              State('pwd-box', 'value')
              )
def success(pid, n_clicks, n_submit_pwd, input1):
    print('pid', pid)
    user = User.query.filter_by(username=pid).first()
    print(user)
    if user:
        if check_password_hash(user.password, input1):
            if n_clicks:
                login_user(user)
                return '/success', html.Div('')
            else:
                pass
        else:
            return '/login', html.Div('Incorrect password')
    else:
        return '/login', html.Div('Please select a valid PID')

# if the password and pid not match

# @app.callback(Output('output-state', 'children'),
#               [Input('login-button', 'n_clicks'),
#                Input('uname-box', 'n_submit'),
#                Input('pwd-box', 'n_submit')],
#               [State('uname-box', 'value'),
#                State('pwd-box', 'value')])
# def update_output(n_clicks, n_submit_uname, n_submit_pwd, input1, input2):
#     if n_clicks > 0 or n_submit_uname > 0 or n_submit_pwd > 0:
#         user = User.query.filter_by(username=input1).first()
#         if user:
#             if check_password_hash(user.password, input2):
#                 return ''
#             else:
#                 return 'Incorrect username or password'
#         else:
#             return 'Incorrect username or password'
#     else:
#         return ''
