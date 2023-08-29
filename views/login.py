from dash import dcc, html, Input, Output, State, no_update
from flask_login import logout_user, current_user
from config import config
import os
import dash_bootstrap_components as dbc
from my_server import app, User
from flask_login import login_user
from werkzeug.security import check_password_hash


# get the pid options in the lmtoy_pid_path
def get_pid_option(path):
    return [
        {'label': os.path.basename(folder_name.split('_')[1]), 'value': os.path.basename(folder_name.split('_')[1])}
        for folder_name in os.listdir(path) if
        os.path.isdir(os.path.join(path, folder_name)) and folder_name.startswith('lmtoy_')
    ]


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
            className="container-width",
            children=[
                dcc.Location(id='url_login', refresh=True),
                html.Div([
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
                        id='login-button',
                        style={'pointer-events': 'none', 'opacity': '0.5'}
                    ),
                    html.Br(),
                    html.Div(dbc.Alert(id='output-state', is_open=False, className='alert-warning', duration=3000))
                ]
                ),
            ]
        )
    ]
)


@app.callback(
    Output('pwd-box', 'value'),
    Input('url_login', 'pathname'),
    prevent_initial_call=True
)
def clear_password_on_logout(pathname):
    if pathname == '/logout' and not current_user.is_authenticated:
        logout_user()
        return ''  # Return an empty string to clear the password field
    return no_update  # No update if the condition is not met


# if both pid and password have value then enable the login button
@app.callback(
    Output('login-button', 'style'),
    [
        Input('pid', 'value'),
        Input('pwd-box', 'value')
    ]
)
def disable_login_button(pid, password):
    if pid and password:
        return {'pointer-events': 'auto', 'opacity': '1'}
    return {'pointer-events': 'none', 'opacity': '0.5'}


# if the input password matches the pid password, login to that pid
@app.callback(
    Output('url_login', 'pathname'),
    Output('output-state', 'children'),
    Output('output-state', 'is_open'),
    Input('login-button', 'n_clicks'),
    State('pid', 'value'),
    State('pwd-box', 'value'),
    State('output-state', 'is_open'),
)
def login_state(n_clicks, pid, password, is_open):
    if n_clicks:
        user = User.query.filter_by(username=pid).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return '/account', '', is_open
        else:
            print('invalid password')
            return '/login', 'Invalid password', not is_open
    else:
        return no_update
