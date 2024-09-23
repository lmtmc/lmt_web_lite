from dash import dcc, html, Input, Output, State
from my_server import app
from flask_login import logout_user, current_user
from flask import session
import dash_bootstrap_components as dbc
from views import login, project, help, ui_elements as ui
import argparse
from config_loader import load_config
try :
    config = load_config()
except Exception as e:
    print(f"Error loading configuration: {e}")

prefix = config['path']['prefix']
default_work_lmt = config['path']['work_lmt']

def create_lalyout():
    return html.Div(
        [
            html.Div(id='navbar-container'),
            html.Br(),
            html.Div(id='body-content', className='content-container'),
            # keep track of the current URL, the app will handle the location change without a full page refresh
            dcc.Location(id='url', refresh=False),
            dcc.Store(id='data-store',data={'pid': None, 'runfile': None, 'source': {}, 'selected_row': None, 'work_lmt': None},
                               storage_type='session'),
            dcc.Store(id='auth-store', data={'is_authenticated': False}, storage_type='session')
        ], id='main-container', className='main-container'
    )

app.layout = create_lalyout()


# update the body-content children based on the URL

@app.callback(
    [Output('navbar-container', 'children'),
     Output('body-content', 'children'),
     Output('auth-store', 'data')],
    [Input('url', 'pathname')],
    [State('auth-store', 'data')]
)
def update_page(pathname, auth_data):
    is_authenticated = current_user.is_authenticated
    auth_data['is_authenticated'] = is_authenticated
    username = current_user.username if is_authenticated else None

    navbar = ui.create_navbar(is_authenticated, username)

    if pathname.startswith(prefix):
        route = pathname[len(prefix):]

        if route in ['', 'login']:
            content = login.layout if not is_authenticated else dcc.Location(pathname=f'{prefix}project',
                                                                             id='redirect-to-project')
        elif route == 'project':
            content = project.layout if is_authenticated else dcc.Location(pathname=f'{prefix}login',
                                                                           id='redirect-to-login')
        elif route == 'help':
            content = help.layout
        elif route == 'logout':
            if is_authenticated:
                logout_user()
                session.clear()
                auth_data['is_authenticated'] = False
            content = dcc.Location(pathname=f'{prefix}login', id='redirect-after-logout')
        else:
            content = html.Div('404 - Page not found')
    else:
        content = html.Div('404 - Page not found')

    if not is_authenticated and content not in [login.layout, help.layout]:
        content = dcc.Location(pathname=f'{prefix}login', id='redirect-to-login')

    return navbar, content, auth_data

server = app.server

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Run the Dash app")
    parser.add_argument("-p", "--port", type=int, default=8000,
                        help="Port to run the Dash app on")
    args = parser.parse_args()
    try:
        app.server.run(port=args.port, debug=True)
    except Exception as e:
        print(e)
        app.server.run(port=args.port, debug=True)