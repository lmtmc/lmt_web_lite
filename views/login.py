# todo password clear after login
from dash import dcc, html, Input, Output, State, no_update
from flask_login import logout_user, current_user
import os
import dash_bootstrap_components as dbc
from my_server import app, User
from flask_login import login_user
from werkzeug.security import check_password_hash
from functions import project_function as pf, logger
from views.ui_elements import Storage
import time
from config import config

logger = logger.logger

prefix = config['path']['prefix']
default_work_lmt = config['path']['work_lmt']
pf.ensure_path_exists(default_work_lmt)

lmtoy_run_path = os.path.join(default_work_lmt, 'lmtoy_run')
pf.ensure_path_exists(default_work_lmt)

pid_options = pf.get_pid_option(lmtoy_run_path)
logger.info(f'pid_options: {pid_options}')

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


# @app.callback(
#     Output('pwd-box', 'value'),
#     # Output(Storage.DATA_STORE.value, 'data', allow_duplicate=True),
#     Input('url_login', 'pathname'),
#     prevent_initial_call=True
# )
# def clear_password_on_logout(pathname):
#     if not current_user.is_authenticated:
#         logger.info(f'Clearing password')
#         return ''  # Return an empty string to clear the password field
#     return no_update  # No update if the condition is not met


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
    Output(Storage.DATA_STORE.value, 'data', allow_duplicate=True),
    Output('pwd-box', 'value'),
    Input('login-button', 'n_clicks'),
    State('pid', 'value'),
    State('pwd-box', 'value'),
    State('output-state', 'is_open'),
    State(Storage.DATA_STORE.value, 'data'),
    prevent_initial_call='initial_duplicate'
)
def login_state(n_clicks, pid, password, is_open, data):
    if not n_clicks:
        return no_update, no_update, no_update, no_update, no_update

    user = User.query.filter_by(username=pid).first()
    if user and check_password_hash(user.password, password):
        login_user(user)
        logger.info(f'Successful login for PID: {pid}')
        data['pid'] = pid
        data['source'] = pf.get_source(default_work_lmt, pid)
        logger.info(f'source for {pid}: {data["source"]}')
        return f'{prefix}/project', '', is_open, data, ''
    else:
        logger.warning(f'Invalid password for PID: {pid}')
        return f'{prefix}/login', 'Invalid password', not is_open, data, ''
