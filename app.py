# index page
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
from server import app
from flask_login import logout_user, current_user
from views import login, login_fd, logout, account, session, joblist_unity

header = html.Div(
    className='header',
    children=html.Div(
        #className='container-width',
        style={'height': '100%'},
        children=[
            html.H4('JOB RUNNER'),
            html.Div(className='links', children=[
                html.A('Current running jobs', href='/joblist_unity'),
                html.Div(id='user-name', className='link'),
                html.Div(id='logout', className='link')
            ]),
        ],

    ),style={'margin':20}
)

app.layout = html.Div(
    [
        header,
        html.Div([
            html.Div(
                html.Div(id='control-content', className='content'),
                className='content-container'
            ),
        ],
            #className='container-width'
            ),

        dcc.Location(id='url', refresh=False),
    ]
)


@app.callback(Output('control-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/':
        return login.layout
    elif pathname == '/login':
        return login.layout
    elif pathname == '/account':
        if current_user.is_authenticated:
            return account.layout
        else:
            return login_fd.layout
    elif pathname == '/session':
        if current_user.is_authenticated:
            return session.layout
        else:
            return login_fd.layout
    elif pathname == '/joblist_unity':
        return joblist_unity.layout
    elif pathname == '/logout':
        if current_user.is_authenticated:
            logout_user()
            return logout.layout
        else:
            return logout.layout
    else:
        return '404'


@app.callback(
    Output('user-name', 'children'),
    Output('logout', 'children'),
    [Input('control-content', 'children')])
def cur_user(input1):
    if current_user.is_authenticated:
        return html.A('Current user: ' + current_user.username, href='/account'), html.A('Logout', href='/logout')
        # 'User authenticated' return username in get_id()
    else:
        return '',''


# @app.callback(
#     Output('logout', 'children'),
#     [Input('control-content', 'children')])
# def user_logout(input1):
#     if current_user.is_authenticated:
#         return html.A('Logout', href='/logout')
#     else:
#         return ''


# export FLASK_ENV=development
if __name__ == '__main__':
    # app.run_server()
    app.server.run(port='8000', debug=True)
