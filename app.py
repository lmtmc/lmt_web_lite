from dash import dcc, html, Input, Output, State, no_update
from my_server import app
from flask_login import logout_user, current_user
from flask import session
import dash_bootstrap_components as dbc
from views import login, project, help, ui_elements as ui, job_status
import argparse
from functions import logger
from config import config

# prefix = '/pipeline'
prefix = config['path']['prefix']
logger = logger.logger

# default_work_lmt = '/home/lmt/work_lmt'
default_work_lmt = config['path']['work_lmt']

app.layout = html.Div(
    [
        ui.navbar,
        html.Br(),
        html.Div(id='body-content', className='content'),
        # keep track of the current URL, the app will handle the location change without a full page refresh
        dcc.Location(id='url', refresh=False),
        html.Div(dcc.Store(id='data-store',
                           data={'pid': None, 'runfile': None, 'source': {}, 'selected_row': None, 'work_lmt': None},
                           storage_type='session'), )
    ]
)


# update the body-content children based on the URL
@app.callback(Output('body-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    user_id = current_user.username if current_user.is_authenticated else None
    logger.info(f'User {user_id} navigating to the page: {pathname}')
    if pathname in [prefix, f'{prefix}login']:
        return login.layout
    elif pathname == f'{prefix}project' and current_user.is_authenticated:
        return project.layout
    elif pathname == f'{prefix}help':
        return help.layout
    elif pathname == f'{prefix}logout':
        if current_user.is_authenticated:
            logout_user()
            session.clear()
            data = {'runfile': None, 'pid': None, 'source': {}, 'selected_row': None, 'work_lmt': default_work_lmt}
            logger.info(f'stored data clear: {data}')
        return login.layout
    elif pathname == f'{prefix}job_status' and current_user.is_authenticated:
        return job_status.layout
    elif not current_user.is_authenticated:
        return dcc.Location(pathname=f'{prefix}login', id='url_redirect')
    else:
        return '404'


# update the navbar
@app.callback(
    [
        Output('user-name', 'children'),
        Output('logout', 'children'),
    ],
    [Input('body-content', 'children')])
def nav_bar(input1):
    if current_user.is_authenticated:

        return [
            dbc.NavLink('Current ProjectId: ' + current_user.username, href=f'{prefix}project'),
            dbc.NavLink('Logout', href=f'{prefix}logout', )
        ]

    else:
        return '', ''


# add callback for toggling the collapse on small screens
@app.callback(
    Output("navbar-collapse", "is_open"),
    [Input("navbar-toggler", "n_clicks")],
    [State("navbar-collapse", "is_open")],
)
def toggle_navbar_collapse(n, is_open):
    if n:
        return not is_open
    return is_open


# add a port arg to the command line
parser = argparse.ArgumentParser(description="Run the Dash app")
parser.add_argument("-p", "--port", type=int, default=8000,
                    help="Port to run the Dash app on")
args = parser.parse_args()

# export FLASK_ENV=development
if __name__ == '__main__':
    logger.info(f'Running the app on port {args.port}')
    try:
        app.server.run(port=args.port, debug=True)
    except Exception as e:
        logger.logger.error(e)
