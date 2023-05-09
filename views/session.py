from dash import dcc, html, Input, Output, State, ctx
import dash_bootstrap_components as dbc
from server import app, User
from flask_login import login_user
from werkzeug.security import check_password_hash
import users_mgt as um
from dash.exceptions import PreventUpdate

# Create app layout
layout = html.Div(children=[
    dcc.Location(id='url_sign_up', refresh=True),
    html.Div(
        className="container",
        children=[
            html.Div(
                html.Div(
                    className="row",
                    children=[
                        html.Div(
                            className="five columns",
                            children=[
                                html.H1('Sign Up'),
                                dcc.Input(id='username-signup', n_submit=0, type='text',
                                          placeholder='Enter username',className='mb-3'),
                                dcc.Input(id='email-signup', n_submit=0, type='email',
                                          placeholder='Enter email', className='mb-3'),
                                dcc.Input(id='password-signup', n_submit=0, type='password',
                                          placeholder='Enter password',className='mb-3'),
                                dcc.Input(id='confirm-password-signup', n_submit=0, type='password',
                                          placeholder='Confirm password',className='mb-2'),
                                html.Button('Submit', n_clicks=0, id='sign-up-submit-button'),
                                html.Br(),
                                html.Div(id='sign-up-message')

                            ]
                        ),

                        # html.Div(children='', id='signup-state'),

                        html.Div(
                            #className="two columns",
                            # children=html.A(html.Button('LogOut'), href='/')
                            children=[
                                html.Br(),
                                html.Div('Already has an account?'),
                                html.A(html.Button('login'), href='/login')
                            ]
                        )
                    ]
                )
            )
        ]
    )
])


@app.callback(Output('sign-up-message', 'children'),
              Output('url_sign_up', 'pathname'),
              [
                  Input('sign-up-submit-button', 'n_clicks'),
                  Input('username-signup', 'n_submit'),
                  Input('email-signup', 'n_submit'),
                  Input('password-signup', 'n_submit'),
                  Input('confirm-password-signup', 'n_submit')],
              [
                  State('username-signup', 'value'),
                  Input('email-signup', 'value'),
                  State('password-signup', 'value'),
                  State('confirm-password-signup', 'value')],
              prevent_initial_call=True
              )
def update_output(sign_up_clicks, n_submit_uname, n_submit_email, n_submit_pwd1, n_submit_pwd2, input1, input2,
                  input3, input4):
    if sign_up_clicks > 0 or n_submit_uname > 0 or n_submit_email > 0 or n_submit_pwd1 > 0 or n_submit_pwd2 > 0:
        user = User.query.filter_by(username=input1).first()
        if user:
            return 'user already exits', '/signup'
        elif input3 == input4:
            um.add_user(input1, input3, input2)
            return '', '/login'
        else:
            return 'password not match', '/signup'
    else:
        raise PreventUpdate
