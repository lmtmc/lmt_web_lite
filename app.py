from dash import dcc, html, Input, Output, State
from my_server import app
from flask_login import logout_user, current_user
from flask import session
import dash_bootstrap_components as dbc
from views import login, account, joblist_unity, project, ui_elements as ui
import argparse

app.layout = html.Div(
    [
        ui.navbar,
        html.Br(),
        html.Div(id='body-content', className='content'),
        # keep track of the current URL, the app will handle the location change without a full page refresh
        dcc.Location(id='url', refresh=False),
        html.Div(ui.data_store)
    ]
)


# update the body-content children based on the URL
@app.callback(Output('body-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    auth_routes = {
        '/account': account.layout,
        '/project': project.layout,
    }
    if pathname in ['/', '/login']:
        return login.layout
    elif pathname in auth_routes and current_user.is_authenticated:
        return auth_routes[pathname]
    elif pathname == '/joblist_unity':
        return joblist_unity.layout
    elif pathname == '/logout':
        if current_user.is_authenticated:
            logout_user()
            session.clear()
        return login.layout
    elif not current_user.is_authenticated:
        return dcc.Location(pathname='/login', id='url_redirect')
    else:
        return '404'


# update the navbar
@app.callback(
    [Output('user-name', 'children'),
     Output('logout', 'children'),
     Output('current-joblist', 'children')],
    [Input('body-content', 'children')])
def nav_bar(input1):
    if current_user.is_authenticated:

        return (dbc.NavLink('Current user: ' + current_user.username, href='/account'),
                dbc.NavLink('Logout', href='/logout', ),
                dbc.NavLink('Current running jobs', href='/joblist_unity'))
    else:
        return '', '', ''


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
    app.server.run(port=args.port, debug=True)
