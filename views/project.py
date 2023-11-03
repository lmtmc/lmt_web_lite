# todo read pix_list as exclude_beam in dataTable and has the options from 0-15
# todo restart and dataverse 0,1,2
# todo update detailed info
# todo display verification
# fix the height, pix_list arrangement
import os
import time
import json

from dash import dcc, html, Input, Output, State, ALL, MATCH, dash_table, ctx, no_update, ClientsideFunction
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
import pandas as pd
from flask_login import current_user
import shutil
from config import config
from my_server import app
from functions import project_function as pf, logger
from views import ui_elements as ui
from views.ui_elements import Session, Runfile, Table, Parameter, Storage

from lmtoy_lite.lmtoy import runs

logger = logger.logger
# Constants
TABLE_STYLE = {'overflow': 'auto'}
HIDE_STYLE = {'display': 'none'}
SHOW_STYLE = {'display': 'block'}

# root directory of the session's working area
# root directory of the session's working area
# default_work_lmt = '/home/lmt/work_lmt'
default_work_lmt = config['path']['work_lmt']
default_session_prefix = os.path.join(default_work_lmt, 'lmtoy_run/lmtoy_')

# default session name
init_session = 'session-0'
# data table column
table_column = ui.table_column

# if any of the update_btn get trigged, update the session list
update_btn = [Session.SAVE_BTN.value, Session.CONFIRM_DEL.value,
              Runfile.DEL_BTN.value, Runfile.SAVE_CLONE_RUNFILE_BTN.value]

layout = html.Div(
    [

        html.Div(ui.url_location),
        dbc.Row(
            [
                dbc.Col(ui.session_layout, width=2),
                dbc.Col(ui.parameter_layout, width=10),
                dcc.Location(id='project_url', refresh=False)

            ]
        )])


# display the sessions
@app.callback(
    [
        Output(Session.SESSION_LIST.value, 'children'),
        Output(Session.MODAL.value, 'is_open'),
        Output(Session.MESSAGE.value, 'children'),
    ],
    [
        Input(Session.NEW_BTN.value, 'n_clicks'),
        Input(Session.SAVE_BTN.value, 'n_clicks'),
        Input(Session.CONFIRM_DEL.value, 'submit_n_clicks'),
        Input(Runfile.CONFIRM_DEL_ALERT.value, 'submit_n_clicks'),
        # Input(Parameter.SAVE_ROW_BTN.value, 'n_clicks'),
        # Input(Parameter.UPDATE_BTN.value, 'n_clicks'),
        Input(Runfile.SAVE_CLONE_RUNFILE_BTN.value, 'n_clicks'),
        Input(Session.SESSION_LIST.value, 'active_item'),

    ],
    [
        State(Session.NAME_INPUT.value, 'value')
    ],
)
def update_session_display(n1, n2, n3, n4, n7, active_session, name):
    logger.info(f'Updating the session list')
    triggered_id = ctx.triggered_id
    logger.debug(f'Triggered: {triggered_id}')

    if not pf.check_user_exists():
        logger.error('User is not authenticated')
        return no_update, no_update, "User is not authenticated"
    pid_path = os.path.join(default_work_lmt, current_user.username)
    if not os.path.exists(pid_path):
        os.mkdir(pid_path)
        logger.error(f'{pid_path} not exist, create a new folder')

    modal_open, message = no_update, ''
    if triggered_id == Session.NEW_BTN.value:
        logger.info(f'Create a new session for user {current_user.username}')
        modal_open = True
    if triggered_id == Session.SAVE_BTN.value:
        default_session_path = default_session_prefix + current_user.username
        new_session_path = os.path.join(pid_path, f'Session-{name}', 'lmtoy_run', f'lmtoy_{current_user.username}')
        if os.path.exists(new_session_path):
            message = f'session-{name} already exists'
        else:
            # Now perform the copy operation.
            shutil.copytree(default_session_path, new_session_path)
            modal_open = False
            message = f"Successfully copied to {new_session_path}"
        logger.info(message)
    elif triggered_id == Session.CONFIRM_DEL.value:
        session_path = os.path.join(pid_path, active_session)
        if os.path.exists(session_path):
            # If it exists, delete the folder and all its contents
            shutil.rmtree(session_path)
            logger.info(f'deleted {session_path}')
        else:
            print(f"The folder {session_path} does not exist.")
    if triggered_id in update_btn:
        time.sleep(1)

    session_list = pf.get_session_list(init_session, pid_path)
    return session_list, modal_open, message


# if click delete session button show the confirmation
@app.callback(
    Output(Session.CONFIRM_DEL.value, 'displayed'),
    Input(Session.DEL_BTN.value, 'n_clicks'),
)
def display_confirmation(n_clicks):
    if ctx.triggered_id == Session.DEL_BTN.value:
        return True
    return False


# display selected runfile
@app.callback(
    [
        Output(Runfile.TABLE.value, 'data', allow_duplicate=True),
        # Output(Runfile.TABLE.value, 'style_data_conditional'),
        Output(Runfile.CONTENT_TITLE.value, 'children'),
        Output(Runfile.PARAMETER_LAYOUT.value, 'style'),
        Output(Storage.DATA_STORE.value, 'data', allow_duplicate=True),
        # Output(Parameter.ACTION.value, 'style'),
    ],
    [
        Input({'type': 'runfile-radio', 'index': ALL}, 'value'),
        Input(Runfile.CONFIRM_DEL_ALERT.value, 'submit_n_clicks'),
        Input(Parameter.SAVE_ROW_BTN.value, 'n_clicks'),
        Input(Parameter.UPDATE_BTN.value, 'n_clicks'),

    ],
    [
        State(Runfile.TABLE.value, "selected_rows"),
        State(Runfile.TABLE.value, 'data'),
        State(Runfile.TABLE.value, 'columns'),
        State(Storage.DATA_STORE.value, 'data'),
        State({'type': 'runfile-radio', 'index': ALL}, 'value'),
    ],
    prevent_initial_call='initial_duplicate'
)
def display_selected_runfile(selected_values, del_runfile_btn, n1, n2, selRow, existing_data,
                             existing_columns, data_store, current_runfile):
    if not ctx.triggered:
        raise PreventUpdate
    # Initialize the DataFrame
    dff = pd.DataFrame(columns=table_column)
    runfile_title = ''
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
    selected_runfile = ''
    parameter_display = HIDE_STYLE
    # detail_value = ''
    # action_style = HIDE_STYLE
    print('current_runfile', current_runfile)
    current_runfile = [value for value in current_runfile if value is not None]
    if current_runfile:
        selected_runfile = current_runfile
        logger.info(f'current_runfile is {current_runfile}')
    logger.info(f'Triggered component to update runfile: {trigger_id}')
    if trigger_id == Parameter.SAVE_ROW_BTN.value or trigger_id == Parameter.UPDATE_BTN.value:
        logger.info(f'Updating the runfile table')

    elif 'runfile-radio' in trigger_id:
        selected_runfile = ctx.triggered[0]['value']
        logger.info(f'Selected runfile: {selected_runfile}')
    if selected_runfile:

        parameter_display = SHOW_STYLE
        # df, runfile_title, highlight = pf.initialize_common_variables(selected_runfile, selRow, init_session)
        runfile_title = pf.get_runfile_title(selected_runfile, init_session)
        df = pf.df_runfile(selected_runfile)
        data_store['runfile'] = selected_runfile
        dff = pd.concat([df, dff])
        if selRow:
            logger.info(f'Selected row: {selRow}')
            data_store['selected_row'] = selRow
            # detail_value = pf.display_row_details(dff.iloc[selRow[0]])
            # action_style = SHOW_STYLE
            highlight = pf.get_highlight(selRow)

        if ctx.triggered_id == Runfile.CONFIRM_DEL_ALERT.value:
            pf.del_runfile(selected_runfile)
    # This seems to be constant, so defined it here
    return dff.to_dict('records'), runfile_title, parameter_display, data_store


# Can not edit the default session
# show runfile delete and clone button after selecting a runfile
# show edit row button after selecting a row
@app.callback(
    [
        Output(Runfile.DEL_BTN.value, 'style'),
        Output(Runfile.CLONE_BTN.value, 'style'),
        Output(Session.DEL_BTN.value, 'style'),
        Output(Session.NEW_BTN.value, 'style'),
        Output(Parameter.DETAIL.value, 'style'),
    ],
    [
        Input(Session.SESSION_LIST.value, 'active_item'),
        Input({'type': 'runfile-radio', 'index': ALL}, 'value'),
        Input(Runfile.TABLE.value, "selected_rows"),
    ],
)
def default_session(active_session, selected_runfile, selected_rows):
    logger.info('active_session: {}, init_session: {}'.format(active_session, init_session))
    selected_runfile = [value for value in selected_runfile if value is not None]
    if not active_session:
        return [HIDE_STYLE] * 5
    # Default all to hide
    runfile_del, runfile_clone, session_del, session_new, detail_parameter = 5 * [HIDE_STYLE]
    if active_session == init_session:
        session_new = SHOW_STYLE
    else:
        session_del = SHOW_STYLE
        if selected_runfile:
            # if selected_runfile[1]:
            runfile_del, runfile_clone = [SHOW_STYLE] * 2
        if selected_rows:
            detail_parameter = SHOW_STYLE

    return runfile_del, runfile_clone, session_del, session_new, detail_parameter


# Define fixed Output objects
fixed_outputs = [
    # Output(Parameter.MODAL.value, 'is_open'),
    Output(Runfile.TABLE.value, 'data'),
]
fixed_states = [

    State(Storage.DATA_STORE.value, 'data'),
    State(Runfile.TABLE.value, 'data'),

]
# Define dynamic Output objects based on a list of field names
field_names = table_column
dynamic_outputs = [Output(field, 'value', allow_duplicate=True) for field in field_names]
dynamic_states = [State(field, 'value') for field in field_names]
# Combine fixed and dynamic Output objects

all_outputs = fixed_outputs + dynamic_outputs
all_states = fixed_states + dynamic_states


# the first element of output is the data of the table, the rest are the parameters
@app.callback(
    all_outputs,
    [
        Input(Table.DEL_ROW_BTN.value, 'n_clicks'),
        Input(Parameter.SAVE_ROW_BTN.value, 'n_clicks'),
        Input(Parameter.UPDATE_BTN.value, 'n_clicks'),
        Input(Runfile.TABLE.value, "selected_rows"),
    ],
    all_states,
    prevent_initial_call=True,
)
def new_job(n1, n2, n3, selected_row, data, df_data, *state_values):
    if df_data:
        logger.info(f'Loading the runfile table to a DataFrame')
        df = pd.DataFrame(df_data)
        df.fillna('', inplace=True)
    else:
        logger.info(f'Creating a new empty DataFrame')
        df = pd.DataFrame(columns=table_column)
    triggered_id = ctx.triggered_id
    logger.info(f'Triggered component to update runfile: {triggered_id}')
    output_values = [''] * (len(table_column) + 1)
    print('selected_row', selected_row)
    if selected_row:
        selected_data = df.loc[selected_row[0]]

        output_values[1:] = pf.table_layout([selected_data[col] for col in table_column])

        if triggered_id == Table.DEL_ROW_BTN.value:
            logger.info(f'Deleting row {selected_row[0]}')
            df.drop(df.index[selected_row[0]], inplace=True)
            pf.save_runfile(df, data['runfile'])
        elif triggered_id in [Parameter.SAVE_ROW_BTN.value, Parameter.UPDATE_BTN.value]:
            # if there are more obsnums then join them using ' '
            parameters = pf.layout_table(list(state_values))
            new_row = {key: value for key, value in zip(table_column, parameters)}
            logger.debug(f'New row: {new_row}')
            if triggered_id == Parameter.SAVE_ROW_BTN.value:
                # add new row to the end of the table
                logger.info(f'Adding new row to the end of the table')
                df = df._append(new_row, ignore_index=True)
            else:
                logger.info(f'Updating row {selected_row[0]}')
                df.iloc[selected_row[0]] = new_row
            pf.save_runfile(df, data['runfile'])
    output_values[0] = df.to_dict('records')
    # logger.debug(f'Updated table values: {output_values}')
    return output_values


# if click delete button show the confirmation
@app.callback(
    Output(Runfile.CONFIRM_DEL_ALERT.value, 'displayed'),
    Input(Runfile.DEL_BTN.value, 'n_clicks'),
    prevent_initial_call=True
)
def display_confirmation(n_clicks):
    return ctx.triggered_id == Runfile.DEL_BTN.value


# open a modal if clone-runfile button
@app.callback(
    [
        Output(Runfile.CLONE_RUNFILE_MODAL.value, 'is_open'),
        Output(Runfile.SAVE_CLONE_RUNFILE_STATUS.value, 'children'),
        Output(Runfile.SAVE_CLONE_RUNFILE_STATUS.value, 'is_open'),
    ],
    [
        Input(Runfile.CLONE_BTN.value, 'n_clicks'),
        Input(Runfile.SAVE_CLONE_RUNFILE_BTN.value, 'n_clicks'),
    ],
    [
        State(Storage.DATA_STORE.value, 'data'),
        State(Runfile.TABLE.value, 'derived_virtual_data'),
        State(Runfile.NAME_INPUT.value, 'value'),
    ],

    prevent_initial_call=True
)
def copy_runfile(n1, n2, data_store, virtual_data, new_name):
    modal_open = False
    status = False
    message = ''
    triggered_id = ctx.triggered_id
    if triggered_id == Runfile.CLONE_BTN.value:
        modal_open = True
    if triggered_id == Runfile.SAVE_CLONE_RUNFILE_BTN.value:
        runfile_to_clone = data_store.get('runfile', '')
        new_runfile_name = f"{current_user.username}.{new_name}"
        new_runfile_path = os.path.join(os.path.dirname(runfile_to_clone), new_runfile_name)
        pf.save_runfile(pd.DataFrame(virtual_data), new_runfile_path)
        message = f'Runfile {new_runfile_name} saved successfully!'
    return modal_open, message, status


# open an alert to submit
@app.callback(
    [
        Output(Runfile.VALIDATION_ALERT.value, 'is_open'),
        Output(Runfile.VALIDATION_ALERT.value, 'children'),
        Output(Runfile.VALIDATION_ALERT.value, 'color'),
    ],
    Input(Runfile.RUN_BTN.value, 'n_clicks'),
    State(Storage.DATA_STORE.value, 'data'),
    prevent_initial_call=True
)
def submit_runfile(n, data_store):
    if ctx.triggered_id != Runfile.RUN_BTN.value or not data_store.get('runfile'):
        return no_update, no_update, no_update
    color = 'danger'
    message = runs.verify(data_store['runfile'], debug=False)
    logger.info(f'Verifying runfile: {data_store["runfile"]}, message: {message}')
    if message is None:
        message = 'Runfile is valid!'
        color = 'success'

    return True, message, color


# if login get the options for source and obsnums
@app.callback(
    [
        Output(Parameter.SOURCE_DROPDOWN.value, 'options'),
        Output(Storage.DATA_STORE.value, 'data'),
    ],
    [
        # Input(Table.NEW_ROW_BTN.value, 'n_clicks'),
        # Input(Table.EDIT_ROW_BTN.value, 'n_clicks'),
        Input(Session.SESSION_LIST.value, 'active_item'),
    ],
    State(Storage.DATA_STORE.value, 'data'),
)
def update_options(active_item, stored_data):
    if not pf.check_user_exists():
        return no_update
    if stored_data['source']:
        sources = stored_data['source']
        source_options = [{'label': source, 'value': source} for source in sources]
    else:
        print('No source file found')

    return source_options, stored_data


# If the source dropdown is changed, update the obsnum dropdown
@app.callback(
    Output(Parameter.OBSNUM_DROPDOWN.value, 'options'),
    Input(Parameter.SOURCE_DROPDOWN.value, 'value'),
    State(Storage.DATA_STORE.value, 'data'),
    prevent_initial_call=True
)
def update_obsnum_options(selected_source, stored_data):
    if not pf.check_user_exists() or not selected_source:
        return no_update
    obsnums = stored_data['source'][selected_source]
    options = [{'label': obsnum, 'value': str(obsnum)} for obsnum in obsnums]
    return options


# source and obsnum can't be None
@app.callback(
    Output('source-alert', 'is_open'),
    Output('source-alert', 'children'),
    Input(table_column[0], 'value'),
    Input(table_column[1], 'value'),
)
def source_exist(source, obsnum):
    if source is None:
        return True, 'Please select a source!'
    elif obsnum is None:
        return True, 'Please select one or more obsnum!'
    else:
        return False, ''


@app.callback(
    [
        Output(table_column[3], 'value'),
        Output(table_column[3], 'options'),
    ],
    [
        Input('all-beam', 'n_clicks'),
        Input(table_column[3], 'value')
    ],
    [State(table_column[3], 'options'), ],
    prevent_initial_call=True
)
def select_all_beam(n_clicks, current_values, options):
    all_values = [option['value'] for option in options]

    if ctx.triggered_id == 'all-beam':
        if set(current_values) == set(all_values):  # if all are selected, unselect all
            current_values = []
        else:  # otherwise, select all
            current_values = all_values
    # Apply the strike-through class to selected options
    for option in options:
        if option['value'] in current_values:
            option['label']['props']['className'] = 'strike-through'
        else:
            option['label']['props']['className'] = None

    return current_values, options


# make modal draggable
app.clientside_callback(
    # ClientsideFunction(namespace='clientside', function_name='make_draggable'),
    '''
    function(is_open) {
    return dash_clientside.clientside.make_draggable(is_open);}
    ''',
    Output("js-container", "children"),
    [Input("draggable-modal", "is_open")],
)
