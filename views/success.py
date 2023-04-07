# Dash configuration
from dash import dcc, html, Input, Output, State, ALL, MATCH
import dash_bootstrap_components as dbc
from server import app
import subprocess
import os
from config import config

lmt_work_path = config['path']['lmt_work']
subfolders = [f.path for f in os.scandir(lmt_work_path) if f.is_dir()]
PID_options = []

for subfolder in subfolders:
    folder_name = os.path.basename(subfolder)
    if folder_name.startswith('lmtoy_'):
        subfolder = folder_name.split('_')[1]
        PID_options.append(os.path.basename(subfolder))
        # print('PID_options', PID_options)

choose_pid_layout = html.Div(
    className="container",
    children=[
        html.Div('Choose a PID: '),
        dcc.Dropdown(
            id='pid',
            options=PID_options,
        ),
        html.Br(),
        html.Button(id='next-button', children='next', n_clicks=0)
    ])
run_files_layout = html.Div(
    dbc.Modal([dbc.ModalTitle('Run file'),
               dbc.ModalBody(dbc.Spinner(color='primary', type='grow'),
                             id='run-file-output', style={'overflowY': 'auto'}),
               dbc.ModalFooter(
                   html.Button('Close', id='close', className='ml-auto')
               )], id='run-file', size='xl', is_open=False)
)


def run_command(python_file):
    result = subprocess.run(['python', python_file], capture_output=True, text=True)
    # checks if the command ran successfully(return code 0)
    if result.returncode == 0:
        output = result.stdout  # converts the stdout string to a regular string
    else:
        output = result.stderr.decode()  # convert the error message to a string
    return output


# Create success layout
layout = html.Div(children=[
    dcc.Location(id='url_login_success', refresh=True),
    choose_pid_layout,
    run_files_layout,
    dcc.Store(id='store')
])


@app.callback(
    Output('run-file-output', 'children'),
    [Input('pid', 'value'),
     Input('run-file', 'is_open')],
    prevent_initial_call=True)
def run_file(pid, is_open):
    if is_open:
        run_path = lmt_work_path + '/lmtoy_' + pid + '/mk_runs.py'

        # result = subprocess.run['python3', run_path]
        output = run_command(run_path)

        return html.Pre(output)


@app.callback(
    Output('run-file', 'is_open'),
    [Input('next-button', 'n_clicks'), Input('close', 'n_clicks')],
    [State('run-file', 'is_open')]
)
def toggle_modal(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open

# layout = html.Div(children=[
#     dcc.Location(id='url_login_success', refresh=True),
#     html.Div(
#         className="container",
#         children=[
#             html.Div(
#                 html.Div(
#                     className="row",
#                     children=[
#                         html.Div(
#                             className="five columns",
#                             children=[
#                                 html.Div('Choose a PID: '),
#                                 dcc.Dropdown(
#                                     options = PID_options,
#                                 )
#
#                             ]
#                         ),
#                         # html.Div(
#                         #     className="five columns",
#                         #     children=[
#                         #         dbc.Label('Select a session'),
#                         #         dcc.Dropdown(
#                         #             ["session1", "session2", "create a new session"],
#                         #             id='session-list'),
#                         #         html.Div(id='select-output'),
#                         #         dbc.Modal(
#                         #             [
#                         #                 dbc.Label("Create a new session"),
#                         #                 dbc.ModalBody(
#                         #                     [dcc.Input(id='add-session'),
#                         #                      html.Button('Add', id='add-btn'),
#                         #                      ]),
#                         #                 dbc.ModalFooter(
#                         #                 html.Button(
#                         #                         "Close", id="close-btn", className="ms-auto"),
#                         #                 ),
#                         #
#                         #             ],
#                         #             id='session-modal',
#                         #             is_open=False,
#                         #             centered=True,
#                         #             size='lg'
#                         #
#                         #         )
#                         #
#                         #     ]
#                         # ),
#
#                         html.Div(
#                             className="two columns",
#                             children=[
#                                 html.Br(),
#                                 html.Button(id='next-button', children='next', n_clicks=0)
#                             ]
#                         ),
#                         dcc.Store(id='store')
#                     ]
#                 )
#             )
#         ]
#     )
# ])


# Create callbacks
# @app.callback(Output('url_login_success', 'pathname'),
#               [Input('back-button', 'n_clicks')])
# def logout_dashboard(n_clicks):
#     if n_clicks > 0:
#         return '/'


# @app.callback(
#     Output('session-modal', 'is_open'),
#     Input('session-list', 'value'),
#     Input('close-btn', 'n_clicks'),
#     Input('add-btn', 'n_clicks'),
#     State('session-modal', 'is_open')
# )
# def show_output(input, n1, n2, is_open):
#     if input == 'create a new session' or n1 or n2:
#         return not is_open
#
#     return is_open

# @app.callback(
#     Output('select-output', 'children'),
#     Input('session-list', 'value'),
#     Input('add-session', 'value'),
#     Input('add-btn', 'n_clicks')
# )
# def display_new_session(input1, input2, n):
#     if input1 != 'create a new session':
#         return f"{input1} added"
#     elif n:
#         return f"{input2} added"
