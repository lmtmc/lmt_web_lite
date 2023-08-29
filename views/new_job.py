from dash import dcc, html, Input, Output, State, ALL, MATCH, dash_table, ctx, no_update
import dash_bootstrap_components as dbc
from config import config
import ast
import json
from my_server import app

beam_options = [{'label': str(i), 'value': str(i)} for i in range(0, 16)]
beam_options.append({'label': 'All beams', 'value': 'all'})
beam_value = config['beam']['value']

obsnum_options_raw = ast.literal_eval(config['obsnum']['options'])
obsnum_options = [{'label': option, 'value': option} for option in obsnum_options_raw]
obsnum = config['obsnum']['value']

with open('./default.json', 'r') as file:
    birdies = config['birdies']['value']
    rums_cut = config['rums_cut']['value']
    syype = ast.literal_eval(config['syype']['value'])
    otf_cal = ast.literal_eval(config['otf_cal']['value'])


def create_label_input_pair(label_text, input_component):
    return html.Div([dbc.Label(label_text, className='me-2'), input_component])


def create_section(label, content):
    return html.Div([dbc.Label(label, className='large-label'), content], style={'margin-bottom': '20px'})


def create_obsnum_parameters(obsnum_options, obsnum):
    return html.Div(
        dcc.Dropdown(id='obsnum', options=obsnum_options, value=obsnum, multi=True),
    )


def create_test_parameters():
    return html.Div(dbc.Row([
        dbc.Col([dbc.Label('_s'),dcc.Input(id='_s')],),
        dbc.Col([dbc.Label('speczoom'), dcc.Input(id='speczoom')], ),
        dbc.Col([dbc.Label('srdp'), dcc.Input(id='srdp')], ),
        dbc.Col([dbc.Label('admit'), dcc.Input(id='admit')], )
    ]))


def create_beam_parameters(beam_options, beam_value):
    return html.Div(
        # dbc.Label('Select which beam', className='large-label'),
        dbc.Row([
            dbc.Col(dbc.Checklist(options=beam_options, inline=True, value=beam_value), width=4),
            dbc.Col([dbc.Label('Time Range'),
                     dcc.Slider(min=0, max=10, step=0.5)])
        ]),
    )


def create_baseline_parameters(input_fields_1, input_fields_2):
    return html.Div([dbc.Row([
        dbc.Col(dbc.Label('Detailed Selection')),
        dbc.Col(dbc.Row(input_fields_1)),
        dbc.Col(
            dbc.Row([
                dbc.Label('Baseline Order', className='me-2'),
                dcc.Input(type='number', min=0, max=10, step=1, style={'width': '100px'})
            ])
        ),
    ]),
        html.Br(),
        dbc.Row([
            dbc.Col(dbc.Label('dv, dw around vlsr')),
            dbc.Col(dbc.Row(input_fields_2)),
            dbc.Col()
        ])])


def create_input_field(label_text, input_id, value, input_type='number', min_val=0, max_val=10, step=0.1, ):
    return dbc.Col([
        dbc.Label(label_text, className='me-2'),
        dbc.Input(id=input_id, value=value, type=input_type, min=min_val, max=max_val, step=step, )
    ])


values_dict1 = {
    'b_regions': 1,
    'l_regions': 1,
    'slice': 1,
}
values_dict2 = {
    'dvs': 2,
    'dw': 2,
}
input_fields_1 = [create_input_field(field, input_id=field, value=values_dict1[field]) for field in
                  ['b_regions', 'l_regions', 'slice']]
input_fields_2 = [
    create_input_field(field, input_id=field, input_type=None, min_val=None, max_val=None, value=values_dict2[field])
    for field in
    ['dvs', 'dw']]

values_dict3 = {
    '_s': 3,
    'speczoom': 3,
    'srdp': 2,
    'admit': 2
}

input_fields_3 = [create_input_field(field, input_id=field, value=values_dict3[field]) for field in
                  ['_s', 'speczoom', 'srdp', 'admit']]


def create_calibration_parameters(birdies, rums_cut, syype, otf_cal):
    return dbc.Row([
        dbc.Col(create_label_input_pair('birdies', dbc.Input(id='birdies', value=birdies))),
        dbc.Col(create_label_input_pair('rms_cut', dbc.Input(id='rums_cut', value=rums_cut))),
        dbc.Col(create_label_input_pair('stype', dbc.RadioItems(options=[1, 0, 2], value=syype, inline=True))),
        dbc.Col(create_label_input_pair('otf_cal', dbc.RadioItems(options=[0, 1], value=otf_cal, inline=True))),
    ])


def create_gridding_parameters():
    return dbc.Row([
        dbc.Col(create_label_input_pair('Map Extent', dbc.Input())),
        dbc.Col(create_label_input_pair('Resolution', dbc.Input())),
        dbc.Col(create_label_input_pair('Cell', dbc.Input())),
        dbc.Col(create_label_input_pair('otf_select',
                                        dbc.RadioItems(options=['jinc', 'gauss', 'triangle', 'box'], inline=True))),
        dbc.Col(create_label_input_pair('RMS_weighted', dbc.Checklist(options=['yes'], inline=True))),
    ])


def create_output_parameters():
    return dbc.Checklist(options=['restart', 'admit', 'maskmoment', 'Dataverse', 'Cleanup after run'], inline=True)


sections = [
    create_section('Select obsnums', create_obsnum_parameters(obsnum_options, obsnum)),
    # create_section('test', html.Div(input_fields_3)),
    create_section('test', create_test_parameters()),
    create_section('Select which beam', create_beam_parameters(beam_options, beam_value)),
    create_section('Baseline and spectral', create_baseline_parameters(input_fields_1, input_fields_2)),
    create_section('Calibration', create_calibration_parameters(birdies, rums_cut, syype, otf_cal)),
    create_section('Gridding', create_gridding_parameters()),
    create_section('Advanced output', create_output_parameters())
]

layout = html.Div(
    dbc.Card([
        dbc.CardHeader('New Job Parameters'),
        dbc.CardBody(sections),
        dbc.Alert(id='new-job-save', is_open=False, duration=1000)
    ]),
    # className='container-width'
)

# @app.callback(
#     Output('new-job-save', 'children'),  # Just a dummy output to trigger the callback
#     Output('new-job-save', 'is_open'),
#     Input('ok-btn', 'n_clicks'),  # Triggered when the "Save" button is clicked
#     State('birdies', 'value'),  # Input value from the 'birdies' field
#     State('rums_cut', 'value'),  # Input value from the 'rums_cut' field
#     # Add more State for other input values as needed
# )
# def save_inputs(n_clicks, birdies_value, rums_cut_value):
#     if ctx.triggered_id == "ok-btn":
#         print(birdies_value, rums_cut_value)
#         data_to_save = {
#             'birdies': birdies_value,
#             'rums_cut': rums_cut_value,
#             # Add other inputs as needed
#         }
#
#         with open('inputs.json', 'w') as file:
#             json.dump(data_to_save, file)
#
#         return "Saved!", True  # Return a message that the values were saved (or any other action you want to take)
#     else:
#         return "", False
