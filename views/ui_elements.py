# slider and checklist cause issue
from dash import dcc, html, Input, Output, State, ALL, MATCH, dash_table, ctx, no_update
import dash_bootstrap_components as dbc
from flask_login import current_user
from functions import project_function as pf
from enum import Enum


class Session(Enum):
    NAME_INPUT = 'session-name'
    MESSAGE = 'session-message'
    SESSION_LIST = 'session-list'
    SAVE_BTN = 'new-session-save'
    MODAL = 'new-session-modal'
    NEW_BTN = 'new-session'
    DEL_BTN = 'del-session'
    CONFIRM_DEL = 'confirm-del-session'
    DEL_ALERT = 'session-del-alert'


class Runfile(Enum):
    TABLE = 'runfile-table'
    CONTENT_TITLE = 'runfile-content-title'
    DEL_BTN = 'del-runfile'
    CLONE_BTN = 'clone-runfile'
    SAVE_BTN = 'runfile-save'
    VALIDATION_ALERT = 'validation-message'
    CONFIRM_DEL_ALERT = 'confirm-del-runfile'
    SAVE_TABLE_BTN = 'save-table'
    RUN_BTN = 'run-btn'
    SAVE_CLONE_RUNFILE_BTN = 'save-clone-runfile'
    SAVE_CLONE_RUNFILE_STATUS = 'save-clone-runfile-status'
    CLONE_RUNFILE_MODAL = 'clone-runfile-modal'
    PARAMETER_LAYOUT = 'parameter'
    NAME_INPUT = 'clone-input'


class Table(Enum):
    # Add Datatable related IDs here
    EDIT_ROW_BTN = 'edit-row'
    DEL_ROW_BTN = 'del-row'
    NEW_ROW_BTN = 'new-row'


# columns_list from runfile
column_list = [
    # Section1
    '_s',  # 0 dropdown (signle selection)
    'obsnum(s)',  # 1 dropdown based on selected source (multiselection)

    # Section2: Select which beam
    'bank',  # 2 radiobutton (bank 1 or bank 2)
    'px_list',  # 3 with all checklist (0-15) and an all beam?
    'time_range',  # 4 a slider
    # Section3: Select baseline and spectral range
    # baseline
    'b_regions',  # 5 input box
    'l_regions',  # 6 input box
    'slice',  # 7 input box
    'baseline_order',  # 8 number inputbox
    # dv dw around vlsr
    'dv',  # 9 input box
    'dw',  # 10 input box
    # Section4: Calibration
    'birdie',  # 11 input box
    'rms_cut',  # 12 input box
    'stype',  # 13 radio button 1 0 2
    'otf_cal',  # 14 radio button 0 1
    # Section5: Gridding
    'extend',  # 15 label input Map Extent
    'resolution',  # 16 label input Resolution
    'cell',  # 17 label input cell
    'otf_select',  # 18 radio button jinc gauss triangle box
    'RMS',  # 19 RMS weighted checkbox yes
    # Section6: Advance Output
    'restart',  # 20 checkbox
    'admit',  # 21
    'maskmoment',  # 22
    'dataverse',  # 23
    'cleanup',  # 24
    # Section7: Others
    'edge',  # 25
    'speczoom',  # 26
    'badcb',  # 27
    'srdp',  # 28

]
# change the column name from px_list to beam
table_column = column_list
table_column[3] = 'beam'


class Parameter(Enum):
    UPDATE_BTN = 'update-row'
    SAVE_ROW_BTN = 'save-row'
    MODAL = 'draggable-modal'
    SOURCE_DROPDOWN = '_s'
    OBSNUM_DROPDOWN = 'obsnum(s)'


class Storage(Enum):
    DATA_STORE = 'data-store'
    URL_LOCATION = 'url_session1'


session_height = '600px'
parameter_body_height = '500px'
# UI Elements
data_store = dcc.Store(id='data-store', data={'runfile': None}, storage_type='session'),
url_location = dcc.Location(id='url_session1', refresh=True),

# Generate column data dynamically
columns = [{"name": col, "id": col, 'hideable': True, 'resizable': True}
           for col in column_list]

runfile_table = dash_table.DataTable(
    id=Runfile.TABLE.value,
    row_selectable='single',
    data=[],
    filter_action="native",
    columns=columns,
    style_cell={
        'textAlign': 'left',
        'font-size': '15px',
        'whiteSpace': 'normal',
        'maxWidth': 125,
    },
    style_table={
        'min-height': '400px',
        'overflowX': 'auto'
    },
    style_header={
        'fontWeight': 'bold',
    },
)

session_modal = pf.create_modal(
    'Create a new session',
    [
        dbc.Input(id=Session.NAME_INPUT.value, placeholder='Enter a session number', min=0, max=100, step=1, type='number'),
        html.Div(id=Session.MESSAGE.value)
    ],
    html.Button("Save", id=Session.SAVE_BTN.value, className="ml-auto"),
    'new-session-modal'
)
session_layout = dbc.Card(
    [
        dbc.CardBody(
            [
                html.Div(dbc.Accordion(id=Session.SESSION_LIST.value,
                                       flush=True,
                                       persistence=True,
                                       persistence_type="session",
                                       active_item='session_0', style={'overflow': 'auto'})),
                session_modal,
                html.Div(dcc.ConfirmDialog(
                    id=Session.CONFIRM_DEL.value,
                    message='Are you sure you want to delete the session?'
                ), style={'position': 'relative', "top": "100px"}),
            ], style={'overflow': 'auto', 'max-height': session_height}),

        dbc.CardFooter(dbc.Row([
            dbc.Col(html.Button([html.I(className="fas fa-trash me-2"), 'Delete Session'],
                                id=Session.DEL_BTN.value, style={'margin-left': 'auto'},
                                className='ms-auto'), width='auto'),
            dbc.Col(html.Button([html.I(className="fa-solid fa-clone me-2"), 'Clone Session'],
                                id=Session.NEW_BTN.value, style={'margin-left': 'auto'},
                                className='ms-auto'), width='auto')
        ], align='center', justify='end'
        ), ),
    ], style={'height': session_height},

)
# parameter layout
bank_options = [
    {'label': '0', 'value': '0'},
    {'label': '1', 'value': '1'},
    {'label': 'Not Apply', 'value': ''},
]
beam_options = [{'label': html.Div(str(i)), 'value': str(i)} for i in range(0, 16)]

radio_select_options = [{'label': '1', 'value': 1}, {'label': '0', 'value': 0}]


def create_input_field(label_text, input_id, input_type='number', min_val=0, max_val=10, step=0.1, ):
    return dbc.Col([
        dbc.Label(label_text, className='me-2'),
        dbc.Input(id=input_id, type=input_type, min=min_val, max=max_val, step=step, )
    ])


def create_label_input_pair(label_text, input_component):
    return html.Div([dbc.Label(label_text, className='me-2'), input_component])


input_fields_1 = [create_input_field(field, input_id=field, ) for field in
                  column_list[5:8]]
input_fields_2 = [
    create_input_field(field, input_id=field, input_type=None, min_val=None, max_val=None, )
    for field in column_list[9:11]]

# todo add components
edit_parameter_layout = [
    html.Div([
        dbc.Label('Select Source', className='large-label'),
        dcc.Dropdown(id=column_list[0], multi=False),
        dbc.Alert(id='source-alert', color='danger', duration=2000)
    ], style={'margin-bottom': '20px'}),

    html.Div([
        dbc.Label('Select Obsnums', className='large-label'),
        dcc.Dropdown(id=column_list[1], clearable=False, multi=True)
    ], style={'margin-bottom': '20px'}),

    html.Div([
        dbc.Label('Beam', className='large-label'),
        dbc.Row([
            dbc.Col([dbc.Label('Bank'), dbc.RadioItems(id=column_list[2], options=bank_options, inline=True)], ),
            dbc.Col([
                dbc.Row([
                    dbc.Col(dbc.Label('Exclude Beams'), width={"size": 'auto', "offset": 0}),
                    dbc.Col(dbc.Button('Select All', id='all-beam', size='sm', color='info'),
                            style={'display': 'flex', 'justify-content': 'flex-end'})
                ]),
                dbc.Row([
                    dbc.Col(dbc.Checklist(id=column_list[3], options=beam_options,
                                          inline=True), width=12)
                ]),

            ]),

            # todo rangeslider not working
            dbc.Col([
                dbc.Label('Time Range'),
                dcc.Input(id=column_list[4], type='text', placeholder='min, max'),

            ]),

        ], style={'margin-bottom': '20px'}),
    ]),

    html.Div([
        dbc.Label('Select baseline and spectral range', className='large-label'),
        html.Div([dbc.Row([
            dbc.Col(dbc.Label('Detailed Selection')),
            dbc.Col(dbc.Row(input_fields_1)),
            dbc.Col(
                dbc.Row([
                    dbc.Label('Baseline Order', className='me-2'),
                    dcc.Input(id=column_list[8], type='number', min=0, max=10, step=1, style={'width': '100px'})
                ])
            ),
        ]),
            html.Br(),
            dbc.Row([
                dbc.Col(dbc.Label('dv, dw around vlsr')),
                dbc.Col(dbc.Row(input_fields_2)),
                dbc.Col()
            ])])

    ], style={'margin-bottom': '20px'}),

    html.Div([
        dbc.Label('Calibration', className='large-label'),
        dbc.Row([
            dbc.Col(html.Div([dbc.Label('birdies', className='me-2'), dbc.Input(id=column_list[11])])),
            dbc.Col(html.Div([dbc.Label('rms_cut', className='me-2'), dbc.Input(id=column_list[12])])),
            dbc.Col(html.Div(
                [dbc.Label('stype', className='me-2'),
                 dbc.RadioItems(options=[1, 0, 2], inline=True, id=column_list[13])])),
            dbc.Col(html.Div(
                [dbc.Label('otf_cal', className='me-2'),
                 dbc.RadioItems(options=[0, 1], inline=True, id=column_list[14])])),
        ])

    ], style={'margin-bottom': '20px'}),

    html.Div([
        dbc.Label('Gridding', className='large-label'),
        dbc.Row([
            dbc.Col(create_label_input_pair('Map Extent', dbc.Input(id=column_list[15]))),
            dbc.Col(create_label_input_pair('Resolution', dbc.Input(id=column_list[16]))),
            dbc.Col(create_label_input_pair('Cell', dbc.Input(id=column_list[17]))),
            dbc.Col(create_label_input_pair('otf_select',
                                            dbc.RadioItems(id=column_list[18],
                                                           options=['jinc', 'gauss', 'triangle', 'box'], inline=True))),
            dbc.Col(create_label_input_pair('RMS_weighted',
                                            dbc.RadioItems(id=column_list[19],
                                                           options=[{'label': 'Yes', 'value': 'yes'},
                                                                    {'label': 'No', 'value': 'no'}], inline=True))),
        ])

    ], style={'margin-bottom': '20px'}),

    html.Div([
        dbc.Label('Advanced Output & others', className='large-label'),
        dbc.Row([
            dbc.Col(
                [dbc.Label('restart'), dbc.RadioItems(id=column_list[20], options=radio_select_options, inline=True)]),
            dbc.Col(
                [dbc.Label('admit'), dbc.RadioItems(id=column_list[21], options=radio_select_options, inline=True)]),
            dbc.Col([dbc.Label('maskmoment'),
                     dbc.RadioItems(id=column_list[22], options=radio_select_options, inline=True)]),
            dbc.Col([dbc.Label('Dataverse'),
                     dbc.RadioItems(id=column_list[23], options=radio_select_options, inline=True)]),
            dbc.Col([dbc.Label('Cleanup after run'),
                     dbc.RadioItems(id=column_list[24], options=radio_select_options, inline=True)]),
        ])
    ],
        style={'margin-bottom': '20px'}),

    html.Div([
        dbc.Label('Advanced Output & others', className='large-label'),
        dbc.Row([
            dbc.Col(create_label_input_pair('edge', dbc.Input(id=column_list[25]))),
            dbc.Col(create_label_input_pair('speczoom', dbc.Input(id=column_list[26]))),
            dbc.Col(create_label_input_pair('badcb', dbc.Input(id=column_list[27]))),
            dbc.Col(create_label_input_pair('srdp', dbc.Input(id=column_list[28]))),

        ]),
    ])

]

runfile_modal = pf.create_modal('Edit parameter',

                                edit_parameter_layout,
                                [
                                    html.Button("Update", id=Parameter.UPDATE_BTN.value, className="ml-auto"),
                                    html.Button("Save new row", id=Parameter.SAVE_ROW_BTN.value, className="ml-auto"),
                                ],
                                Parameter.MODAL.value)
clone_runfile_modal = pf.create_modal('Input the new runfile name',
                                      html.Div([html.Label(current_user.username if current_user else None),
                                                dcc.Input(id=Runfile.NAME_INPUT.value)]),
                                      [
                                          dbc.Alert(id=Runfile.SAVE_CLONE_RUNFILE_STATUS.value, dismissable=True,
                                                    is_open=False),
                                          html.Button("Clone", id=Runfile.SAVE_CLONE_RUNFILE_BTN.value)
                                      ],
                                      Runfile.CLONE_RUNFILE_MODAL.value)
parameter_layout = dbc.Card(
    [
        dbc.CardHeader(
            html.Div([
                html.Div([
                    dbc.Row([
                        dbc.Col(html.Div(id=Runfile.CONTENT_TITLE.value), width='auto'),
                        dbc.Col(html.Div([
                            dbc.Row([
                                dbc.Col(html.Button([html.I(className="fas fa-edit me-2"), 'edit row'],
                                                    id=Table.EDIT_ROW_BTN.value,
                                                    className='me-2'), ),
                                dbc.Col(html.Button([html.I(className="fas fa-trash me-2"), 'delete row'],
                                                    id=Table.DEL_ROW_BTN.value,
                                                    className='me-2')),
                                dbc.Col(html.Button([html.I(className="fas fa-plus me-2"), 'clone row'],
                                                    id=Table.NEW_ROW_BTN.value))
                            ])
                        ], className='d-flex align-items-center justify-content-between')
                        ),
                        dbc.Col(
                            dbc.Row([
                                dbc.Col(html.Button([html.I(className="fas fa-trash me-2"), 'Delete Runfile'],
                                                    id=Runfile.DEL_BTN.value), width='auto'),
                                dbc.Col(html.Button([html.I(className="fa-solid fa-clone me-2"), 'Clone Runfile'],
                                                    id=Runfile.CLONE_BTN.value), width='auto'),
                            ]), width='auto', className='ms-auto')
                    ], align='center', justify='between')
                ])
            ])
        ),
        dbc.CardBody([
            runfile_table,
            html.Div(runfile_modal, style={'max-height':'200px', 'overflowY':'auto'}),
            html.Div(id='js-container'),
            clone_runfile_modal,
            html.Div(dbc.Alert(id=Runfile.VALIDATION_ALERT.value, is_open=False, dismissable=True, duration=3000)),
            html.Br(),
        ],
            # style={'height': parameter_body_height, "overflowY": "auto"}
            ),

        html.Div(dcc.ConfirmDialog(
            id=Runfile.CONFIRM_DEL_ALERT.value,
            message='Are you sure to delete the runfile?'
        ),
            id='confirm-dialog-container',  # Give it an ID for styling
        ),

        dbc.CardFooter([
            html.Div([
                html.Button([html.I(className="fa fa-paper-plane me-2"), 'Submit Job'], id=Runfile.RUN_BTN.value,
                            n_clicks=0),
            ], className='d-flex justify-content-end')
        ])
    ],
    id=Runfile.PARAMETER_LAYOUT.value,
)

link_bar = dbc.Row(
    [
        dbc.Col(id='current-joblist', width='auto'),
        dbc.Col(id='user-name', width='auto'),
        dbc.Col(id='logout', width='auto'),
        dbc.Col(
            dbc.Row(
                [
                    dbc.Col(html.I(className="bi bi-question-circle-fill"), width="auto"),
                    dbc.Col(dbc.NavLink("Help", href="/help"), width="auto"),
                ],
            ),
        )
    ],
    className='ms-auto flex-nowrap mt-3 mt-md-3 me-5', align="center",
)

navbar = dbc.Navbar(
    [
        html.A(
            dbc.Row(
                [dbc.Col(html.Img(src='/assets/lmt_img.jpg', height='30px'), ),
                 dbc.Col(
                     dbc.NavbarBrand('JOB RUNNER', className='ms-2', style={'fontSize': '24px', 'color': 'black'})), ],
                # ms meaning margin start
                align='right',
                className='ms-5'
            ),
            href='/account', style={'textDecoration': 'none'}
        ),
        dbc.NavbarToggler(id='navbar-toggler', n_clicks=0),
        dbc.Collapse(
            link_bar,
            id='navbar-collapse',
            is_open=False,
            navbar=True
        )
    ],
    dark=True
)