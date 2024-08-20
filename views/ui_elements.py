# slider and checklist cause issue
from dash import dcc, html, Input, Output, State, ALL, MATCH, dash_table, ctx, no_update
import dash_bootstrap_components as dbc
from flask_login import current_user
from functions import project_function as pf
from enum import Enum
from config import config

prefix = config['path']['prefix']


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
    SUBMIT_JOB = 'submit-job'
    RUNFILE_SELECT = 'runfile-select'


class Runfile(Enum):
    TABLE = 'runfile-table'
    CONTENT_TITLE = 'runfile-content-title'
    CONTENT = 'runfile-content'
    DEL_BTN = 'del-runfile'
    CLONE_BTN = 'clone-runfile'
    SAVE_BTN = 'runfile-save'
    EDIT_BTN = 'runfile-edit'
    VALIDATION_ALERT = 'validation-message'
    CONFIRM_DEL_ALERT = 'confirm-del-runfile'
    SAVE_TABLE_BTN = 'save-table'
    RUN_BTN = 'run-btn'
    SAVE_CLONE_RUNFILE_BTN = 'save-clone-runfile'
    SAVE_CLONE_RUNFILE_STATUS = 'save-clone-runfile-status'
    CLONE_RUNFILE_MODAL = 'clone-runfile-modal'
    CONTENT_DISPLAY = 'parameter'
    NAME_INPUT = 'clone-input'
    STATUS = 'submit-job-status'


class Table(Enum):
    # Add Datatable related IDs here
    DEL_ROW_BTN = 'del-row'
    CLONE_ROW_BTN = 'clone-row'
    EDIT_TABLE = 'edit-table'
    CONFIRM_DEL_ROW = 'confirm-del-row'
    OPTION = 'table-option'
    ADD_ROW_BTN = 'add-new-row'
    SELECT_ALL = 'select-all-row'
    FILTER_BTN = 'filter-row'


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
    'extent',  # 15 label input Map Extent
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
table_column[3] = 'exclude_beams'


class Parameter(Enum):
    APPLYALL_BTN = 'apply-all'
    SAVE_BTN = 'save-row'
    UPDATE_BTN = 'update-row'
    MODAL = 'draggable-modal'
    TABLE = 'parameter-table'
    DETAIL = 'parameter-detail'
    ACTION = 'parameter-action'
    SOURCE_DROPDOWN = '_s'
    OBSNUM_DROPDOWN = 'obsnum(s)'
    CANCEL_BTN = 'cancel-btn'


class Storage(Enum):
    DATA_STORE = 'data-store'
    URL_LOCATION = 'url_session1'


session_height = '500px'
parameter_body_height = '75vh'
table_height = '35vh'
detail_height = '35vh'
card_height = '28vh'
detail_card_style = {'height': card_height, 'padding': '10px', 'overflowY': 'auto', 'margin': '10px'}


# Generate column data dynamically
columns = [{"name": col, "id": col,
            # toggle table columns
            'hideable': True,
            'resizable': True}
           for col in column_list]

tooltip_header = {
    col: f'{col}' for col in column_list
}

runfile_content = html.Pre(id=Runfile.CONTENT.value, style={'overflowX': 'auto', 'overflowY': 'auto', 'padding': '10px',
                                                            'white-space': 'pre-wrap'})

runfile_table = dash_table.DataTable(
    id=Runfile.TABLE.value,
    row_selectable='multi',
    data=[],
    filter_action="native",
    columns=columns,
    # page_size=5,
    style_cell={
        'textAlign': 'left',
        'font-size': '14px',
        'whiteSpace': 'normal',
        'height': 'auto',
    },
    style_table={
        'maxHeight': table_height,
        'overflowX': 'auto',
        'overflowY': 'auto',
        'minWidth': '100%',
    },
    tooltip_header=tooltip_header,
    style_header={
        'backgroundColor': 'grey',  # dark background
        'color': 'white',  # white text
        'fontWeight': 'bold',  # make the text bold
        # 'border': '1px solid black',  # add a border around the headers
        'textAlign': 'center'  # center-align text
    },
    style_filter={
        'backgroundColor': 'grey',
        'color': 'white'
    },
    tooltip_delay=0,
    tooltip_duration=None,
    fixed_columns={'headers': True, 'data': 2},
)

session_modal = pf.create_modal(
    'Create a new session',
    [
        html.Div(dbc.Input(id=Session.NAME_INPUT.value, placeholder='Enter a session name', type='text',
                           # min=0, max=100, step=1,
                           # type='number'
                           )),
        html.Div(id=Session.MESSAGE.value)
    ],
    html.Button("Save", id=Session.SAVE_BTN.value, className="ml-auto"),
    'new-session-modal'
)

clone_runfile_modal = pf.create_modal('Input the new runfile name',
                                      html.Div([html.Label(current_user.username if current_user else None),
                                                dcc.Input(id=Runfile.NAME_INPUT.value)]),
                                      [
                                          html.Div(id=Runfile.SAVE_CLONE_RUNFILE_STATUS.value,
                                                   style={'display': 'none'}),
                                          html.Button("Clone", id=Runfile.SAVE_CLONE_RUNFILE_BTN.value)
                                      ],
                                      Runfile.CLONE_RUNFILE_MODAL.value)

session_layout = html.Div(
    [
        dbc.Row([
            dbc.Col('Session List', className='mb-4 title-link', id='session-list-title', width=8),
                dbc.Col(
                    dbc.ButtonGroup([
                        dbc.Button('Clone', id=Session.NEW_BTN.value,  outline=True, color='secondary',),
                        dbc.Button('Delete', id=Session.DEL_BTN.value,  outline=True, color='secondary'),
                    ], size='sm', ),
        ),
            ], className='mb-3', align='center'),
        html.Div(
            dbc.Accordion(
                id=Session.SESSION_LIST.value,
                flush=True,
                persistence=True,
                persistence_type="session",
                active_item='session-0',
                style={'overflow': 'auto'}
            ),
            style={'flex-grow': '1', 'overflowY': 'auto', 'padding': '10px'}
        ),


        # Session modal and confirm dialog
        session_modal,
        html.Div(
            dcc.ConfirmDialog(id=Session.CONFIRM_DEL.value, message='')
        ),
        # ButtonGroup at the bottom
        html.Div(
            [dbc.Row([
                dbc.Label('Select runfiles to submit', className='sm-label',),
                dbc.Col(
                    dcc.Dropdown(id = Session.RUNFILE_SELECT.value, multi=True, placeholder='Select Runfiles'),width='auto',
                    className='mb-2'
                ),
                dbc.Col(
                    dbc.ButtonGroup([
                        dbc.Button("Submit Job", id=Runfile.RUN_BTN.value, outline=True, color='secondary'),
                        dbc.Button("Job Status", id='check-job-status', outline=True, color='secondary', disabled=True),
                        dbc.Button('View result', id='view-result', outline=True, color='secondary', disabled=True),


                    ], size='sm', className='ms-auto'),
                    width='auto',
                    className='d-flex justify-content-end'
                ),
                dbc.Col(dcc.Link('Open Result',
                                 href='',
                                 id='view-result-url',
                                 target='_blank',
                                 style={'display': 'none', 'color': 'grey'}),)
            ],
                className='justify-content-between align-items-end',
            ),
            dcc.Markdown(id=Session.SUBMIT_JOB.value, className='submit-job-message')],id='submit-job-section'
        ),

    ],
    id='session-list-display',
    className='session-list-display'
)



runfile_layout = html.Div(
    [
        html.Div('Runfile Content', className='mb-4 title-link', id='runfile-content-title', ),
        html.Div(
            [
                html.Div([
                    html.Div([
                        dbc.Row([
                            # Runfile Content Title
                            dbc.Col(
                                html.Div(id=Runfile.CONTENT_TITLE.value),
                                width='auto'
                            ),
                            # Runfile Options
                            dbc.Col(
                                dbc.ButtonGroup([
                                    dbc.Button(html.I(className='fas fa-edit'), id=Runfile.EDIT_BTN.value,
                                               color='secondary', className='mr-5'),
                                    dbc.Button(html.I(className='fas fa-trash-alt'), id=Runfile.DEL_BTN.value,
                                               color='secondary', className='mr-5'),
                                    dbc.Button(html.I(className='fas fa-clone'), id=Runfile.CLONE_BTN.value,
                                               color='secondary'),
                                ], size='lg'),
                                width='auto'
                            ),
                            dbc.Tooltip("Edit", target=Runfile.EDIT_BTN.value,placement='bottom', className="custom-tooltip"),
                            dbc.Tooltip("Delete", target=Runfile.DEL_BTN.value,placement='bottom',className="custom-tooltip"),
                            dbc.Tooltip("Clone", target=Runfile.CLONE_BTN.value,placement='bottom',className="custom-tooltip"),
                        ], align='center', style={'margin-bottom': '10px'}),
                    ], ),
                ], style={'margin-bottom': '0'}),


                html.Div([



                    html.Div(runfile_content, className='mb-5',
                             style={'border': '1px solid #CCCCCC', 'max-height': session_height,
                                    'overflowY': 'auto',
                                    'padding': '10px', }),
                    html.Div(clone_runfile_modal),
                    html.Div(dcc.ConfirmDialog(
                        id=Runfile.CONFIRM_DEL_ALERT.value,
                        message=''
                    ),
                        id='confirm-dialog-container',  # Give it an ID for styling
                    ),
                ],
                )],
            className='session-list-display'
            #style={'margin': '0', 'border': '1px solid #CCCCCC', 'padding': '10px', 'margin-bottom': '10px',}
        ),

    ], id=Runfile.CONTENT_DISPLAY.value, style={'display': 'none'},
),
# parameter layout
bank_options = [
    {'label': '0', 'value': '0'},
    {'label': '1', 'value': '1'},
    {'label': 'Not Apply', 'value': ''},
]
# make the beam option into four columns
beam_style_1 = {
    'fontSize': '10px',
    'width': '3',
    'marginRight': '5px',

}
beam_style_2 = {
    'fontSize': '10px',
    'width': '3',

}
beam_options_1 = [{'label': html.Div(str(i), style=beam_style_1), 'value': str(i)} for i in range(0, 10)]
beam_options_2 = [{'label': html.Div(str(i), style=beam_style_2), 'value': str(i)} for i in range(10, 16)]
beam_options = beam_options_1 + beam_options_2

radio_select_options = [{'label': ' ', 'value': ''}, {'label': '1', 'value': 1}, {'label': '0', 'value': 0}]


def create_input_field(label_text, input_id, input_type='number', min_val=0, max_val=10, step=0.1, ):
    return dbc.Col([
        dbc.Label(label_text, className='sm-label'),
        dbc.Input(id=input_id, type=input_type, min=min_val, max=max_val, step=step, )
    ], className='mb-3')


def create_label_input_pair(label_text, input_component):
    return html.Div([dbc.Label(label_text, className='sm-label'), input_component])


input_fields_1 = [create_input_field(field, input_id=field, input_type=None, min_val=None, max_val=None, )
                  for field in column_list[5:8]]
input_fields_2 = [
    create_input_field(field, input_id=field, input_type=None, min_val=None, max_val=None, )
    for field in column_list[9:11]]

tooltip_target = ['obsunms_label', 'bank_label', 'b_order_label', 'extent_label']
tooltip_content = [
    "obsnum: A single observation number, typically 6 digits, e.g. 123456, obsnums: a comma separated "
    "series of obsnums to stack observations",
    "Select a bank from a WARES based instrument; -1 means all banks, 0 is the first bank",
    "baseline order of a polynomial baseline subtraction in WARES based instruments",
    "half the size of the (square) box on the sky for gridding (in arcsec)",
]

edit_parameter_layout = html.Div(
    [
        dbc.Row(
            [
                dbc.Col(dbc.Card([dbc.Label('Source and obsnum', className='large-label'),
                                  dbc.Row(
                                      [dbc.Col(dbc.Label('Source', className="sm-label"),
                                               width=4),
                                       dbc.Col(dcc.Dropdown(id=column_list[0], multi=False), width=8),
                                       ], align='center',
                                      className='mb-3'
                                  ),
                                  dbc.Row(
                                      [dbc.Col(dbc.Label('Obsnum', className="sm-label", id=tooltip_target[0]),
                                               width=4),
                                       dbc.Col(
                                           dcc.Dropdown(id=column_list[1], multi=True),

                                           width=8)],
                                      align='center'),
                                  pf.make_tooltip(tooltip_content[0], tooltip_target[0]),
                                  ], style=detail_card_style), width=4, ),
                dbc.Col(dbc.Card([
                    dbc.Label('Beam', className='large-label'),
                    dbc.Row([dbc.Col(dbc.Label('Bank', className='sm-label', id=tooltip_target[1]), width=4),
                             dbc.Col(dcc.Dropdown(id=column_list[2], options=bank_options, ), width=8),
                             pf.make_tooltip(tooltip_content[1], tooltip_target[1]), ], align='center', className='mb-3'

                            ),

                    dbc.Row(
                        [dbc.Col(dbc.Label('Exclude Beams', className='sm-label'), width='auto'),
                         dbc.Col(dbc.Button('Check All', id='all-beam', color='secondary',
                                            style={'padding': '0', 'font-size': '8px', 'height': '20px', }),
                                 width='auto'),
                         ], align='center', className='mb-3'),

                    dbc.Row(dbc.Col(dbc.Checklist(id=column_list[3], options=beam_options, inline=True),
                                    width=8), className='mb-3'),

                    dbc.Row([
                        dbc.Col(dbc.Label('Time Range', className='sm-label'), width=6),
                        dbc.Col(dbc.Input(id=column_list[4], placeholder='min, max'), width=6),
                    ],
                        align='center'
                    ),
                ], style=detail_card_style), width=4),

                dbc.Col(dbc.Card([
                    dbc.Label('Baseline and spectral', className='large-label'),
                    html.Div([
                        dbc.Row([
                            dbc.Col(dbc.Label('Detail', className='sm-label'), width=4),
                            dbc.Col(dbc.Row(input_fields_1)),
                        ], align='center'),
                        dbc.Row([
                            dbc.Col(dbc.Label('Baseline Order', className='sm-label', id=tooltip_target[2]), width=4),
                            dbc.Col(dcc.Input(id=column_list[8], style={'height': '30px', 'width': '75px'}), ),
                            pf.make_tooltip(tooltip_content[2], tooltip_target[2])
                        ], align='center', className='mb-3'),

                        dbc.Row([
                            dbc.Col(dbc.Label('dv, dw around vlsr', className='sm-label'), width=4),
                            dbc.Col(dbc.Row(input_fields_2)),
                        ], align='center')])

                ], style=detail_card_style), width=4)
            ]),
        dbc.Row([
            dbc.Col(dbc.Card([
                dbc.Label('Calibration', className='large-label'),
                dbc.Row([
                    dbc.Col(
                        html.Div([dbc.Label('birdies', className='sm-label', ), dbc.Input(id=column_list[11])])),
                    dbc.Col(html.Div([dbc.Label('rms_cut', className='sm-label'), dbc.Input(id=column_list[12])]))],
                    className='mb-3'),
                dbc.Row([dbc.Col(html.Div(
                    [dbc.Label('stype', className='sm-label'),
                     dbc.RadioItems(options=[1, 0, 2], id=column_list[13])])),
                    dbc.Col(html.Div(
                        [dbc.Label('otf_cal', className='sm-label'),
                         dbc.RadioItems(options=[0, 1], id=column_list[14])])),
                ])

            ], style=detail_card_style), ),

            dbc.Col(dbc.Card([
                dbc.Label('Gridding', className='large-label'),
                dbc.Row([
                    dbc.Col(create_label_input_pair('Map Extent', dbc.Input(id=column_list[15])), id=tooltip_target[3]),
                    dbc.Col(create_label_input_pair('Resolution', dbc.Input(id=column_list[16]))),
                    dbc.Col(create_label_input_pair('Cell', dbc.Input(id=column_list[17]))),
                    pf.make_tooltip(tooltip_content[3], tooltip_target[3])
                ], className='mb-3'),
                dbc.Row([
                    dbc.Col(create_label_input_pair('otf_select',
                                                    dcc.Dropdown(id=column_list[18],
                                                                 options=['jinc', 'gauss', 'triangle', 'box'], ))),
                    dbc.Col(create_label_input_pair('RMS_weighted',
                                                    dbc.RadioItems(id=column_list[19],
                                                                   options=[{'label': 'Yes', 'value': 'yes'},
                                                                            {'label': 'No', 'value': 'no'}],
                                                                   inline=True))),
                ]
                )

            ], style=detail_card_style), ),

            dbc.Col(dbc.Card([
                dbc.Label('Advanced Outputs and others', className='large-label'),
                dbc.Row([
                    dbc.Col([dbc.Label('Restart', className='sm-label'),
                             dcc.Dropdown(id=column_list[20], options=radio_select_options)]),
                    dbc.Col(
                        [dbc.Label('admit', className='sm-label'),
                         dcc.Dropdown(id=column_list[21], options=radio_select_options)]),
                    dbc.Col([dbc.Label('maskmoment', className='sm-label'),
                             dcc.Dropdown(id=column_list[22], options=radio_select_options, )])], className='mb-3'),
                dbc.Row([
                    dbc.Col([dbc.Label('Dataverse', className='sm-label'),
                             dcc.Dropdown(id=column_list[23], options=radio_select_options)]),
                    dbc.Col([dbc.Label('Cleanup after run', className='sm-label'),
                             dcc.Dropdown(id=column_list[24], options=radio_select_options)], )], className='mb-3'),
                dbc.Row([
                    dbc.Col(create_label_input_pair('edge', dbc.Input(id=column_list[25]))),
                    dbc.Col(create_label_input_pair('speczoom', dbc.Input(id=column_list[26]))),
                    dbc.Col(create_label_input_pair('badcb', dbc.Input(id=column_list[27]))),
                    dbc.Col(create_label_input_pair('srdp', dbc.Input(id=column_list[28]))),

                ]),
            ], style=detail_card_style)),
        ], className='mb-3'),
        html.Div(
            dbc.Row([
                dbc.Col(html.Button("Save", id=Parameter.SAVE_BTN.value), width="auto", className="ml-auto"),
                dbc.Col(html.Button("Update", id=Parameter.UPDATE_BTN.value), width="auto", className="ml-auto"),
                dbc.Col(html.Button("Cancel", id=Parameter.CANCEL_BTN.value), width="auto", className="ml-auto"),
            ], className='d-flex justify-content-end mb-2')),
    ])

parameter_layout = dbc.Modal(
    [
        dbc.ModalHeader(html.H5('Edit Parameters')),
        dbc.ModalBody(
            [
                html.Div(
                    [
                        html.Div(
                            [html.H1('Parameter Table', className='mb-4 title-link', id='parameter-table-location'),
                             html.Div(
                                 dbc.ButtonGroup(
                                        [
                                            dbc.Button('Edit rows', id=Table.EDIT_TABLE.value, color='secondary',outline=True ),
                                            dbc.Button('Delete rows', id=Table.DEL_ROW_BTN.value, color='secondary', outline=True),
                                            dbc.Button('Clone Rows', id=Table.CLONE_ROW_BTN.value, color='secondary', outline=True),
                                            dbc.Button('Add a new row', id=Table.ADD_ROW_BTN.value, color='secondary', outline=True),
                                            dbc.Button('Save filtered row', id=Table.FILTER_BTN.value, color='secondary', outline=True),
                                        ], className='d-flex justify-content-end'
                                 ),
                             #     dbc.DropdownMenu(
                             #     label="Table Options",
                             #     children=[
                             #         dbc.DropdownMenuItem("Edit rows", id=Table.EDIT_TABLE.value, ),
                             #         dbc.DropdownMenuItem("Delete rows", id=Table.DEL_ROW_BTN.value, ),
                             #         dbc.DropdownMenuItem("Clone Rows", id=Table.CLONE_ROW_BTN.value, ),
                             #         dbc.DropdownMenuItem('Add a new row', id=Table.ADD_ROW_BTN.value),
                             #         dbc.DropdownMenuItem("Save filtered row", id=Table.FILTER_BTN.value, ),
                             #     ], color='secondary', className='d-flex justify-content-end'
                             # ),
                                 id=Table.OPTION.value, ),
                             dcc.ConfirmDialog(id=Table.CONFIRM_DEL_ROW.value, message='', )
                             ],
                            className='d-flex justify-content-between'),
                        html.Div([html.Div(runfile_table, className='mb-3', ),
                                  html.Button('Select/Deselect all', id=Table.SELECT_ALL.value),
                                  dbc.Alert(id='source-alert', color='danger', is_open=False, )],
                                 style={'margin': '10px', 'border': '1px solid #CCCCCC', 'padding': '10px',
                                        'overflowX': 'auto', }),
                    ], id=Parameter.TABLE.value, className='mb-3',
                    style={'overflow': 'visible', }, ),

                html.Div(
                    [
                        html.Div('Edit Parameters', className='mb-4 title-link', id='parameter-detail-title'),
                        html.Div(edit_parameter_layout,
                                 style={'margin': '0', 'border': '1px solid #CCCCCC', 'padding': '10px',
                                        'margin-bottom': '10px', }),
                    ], id=Parameter.DETAIL.value, className='mb-3', style={'display': 'none'})
            ], style={
                'overflowX': 'auto', 'height': '100vh', 'width': '100%', 'padding': '10px',
                'overflowY': 'auto'
            })
    ], id=Parameter.MODAL.value, is_open=False, scrollable=True, size='xl', centered=True,
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
                    dbc.Col(dbc.NavLink("Help", href=f"{prefix}help"), width="auto"),
                ],
            ),
        )
    ],
    className='ms-auto flex-nowrap mt-3 mt-md-3 me-5', align="center",
)

navbar = html.Div(dbc.Navbar(
    [
        html.A(
            dbc.Row(
                [dbc.Col(html.Img(src=f'{prefix}assets/lmt_img.jpg', height='30px'), ),
                 dbc.Col(
                     dbc.NavbarBrand('JOB RUNNER', className='ms-2', style={'fontSize': '24px', 'color': 'black'})), ],
                # ms meaning margin start
                align='right',
                className='ms-5'
            ),
            href=f'{prefix}assets/lmt_img.jpg', style={'textDecoration': 'none'}
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
),
    style={
        'position': 'fixed',  # This fixes the navbar position
        'top': 0,  # Aligns the navbar to the top of the page
        'left': 0,
        'width': '100%',  # Navbar width is 100% of the page
        'zIndex': 1000  # Ensures navbar stays on top of other elements
    }
)

fixed_states = [State(Runfile.TABLE.value, 'data')]
# Define dynamic Output objects based on a list of field names
field_names = table_column
dynamic_outputs = [Output(field, 'value', allow_duplicate=True) for field in field_names]
dynamic_states = [State(field, 'value') for field in field_names]
# Combine fixed and dynamic Output objects
all_states = fixed_states + dynamic_states