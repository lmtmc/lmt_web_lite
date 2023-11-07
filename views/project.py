# todo read pix_list as exclude_beam in dataTable and has the options from 0-15
# todo restart and dataverse 0,1,2
# todo update detailed info
# todo display verification
# todo change a value in parameter layout, the value in table of all runfiles will change
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
        ui.session_layout,
        html.Br(),
        ui.parameter_layout,
    ])


#
#
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
        Output(Runfile.CONTENT_TITLE.value, 'children'),
        Output(Runfile.PARAMETER_LAYOUT.value, 'style'),
        # Output(Storage.DATA_STORE.value, 'data', allow_duplicate=True),
    ],
    [
        Input({'type': 'runfile-radio', 'index': ALL}, 'value'),
        Input(Runfile.CONFIRM_DEL_ALERT.value, 'submit_n_clicks'),
        Input(Parameter.SAVE_ROW_BTN.value, 'n_clicks'),
        Input(Parameter.UPDATE_BTN.value, 'n_clicks'),

    ],
    [
        State(Runfile.TABLE.value, "selected_rows"),
        # State(Storage.DATA_STORE.value, 'data'),
    ],
    prevent_initial_call='initial_duplicate'
)
def display_selected_runfile(selected_runfile, del_runfile_btn, n1, n2, selRow):
    if not ctx.triggered:
        raise PreventUpdate
    # Initialize the DataFrame
    dff = pd.DataFrame(columns=table_column)
    runfile_title = ''
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
    parameter_display = HIDE_STYLE
    print('selected_runfile', selected_runfile)
    current_runfile = [value for value in selected_runfile if value is not None]
    if current_runfile:
        current_runfile = current_runfile[0]
        parameter_display = SHOW_STYLE
        print('check selected_runfile', current_runfile)
        runfile_title = pf.get_runfile_title(current_runfile, init_session)
        df = pf.df_runfile(current_runfile)
        print('df here', df)
        # data_store['runfile'] = current_runfile
        dff = pd.concat([df, dff])
        # if selRow:
        #     logger.info(f'Selected row: {selRow}')
        #     data_store['selected_row'] = selRow
        if ctx.triggered_id == Runfile.CONFIRM_DEL_ALERT.value:
            pf.del_runfile(current_runfile)
        logger.info(f'current_runfile is {current_runfile}')
    logger.info(f'Triggered component to update runfile: {trigger_id}')

    return dff.to_dict('records'), runfile_title, parameter_display


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
        Output(Parameter.ACTION.value, 'style'),
    ],
    [
        Input(Session.SESSION_LIST.value, 'active_item'),
        Input({'type': 'runfile-radio', 'index': ALL}, 'value'),
        Input(Runfile.TABLE.value, "selected_rows"),
    ],
    prevent_initial_call=True
)
def default_session(active_session, selected_runfile, selected_rows):
    logger.info('active_session: {}, init_session: {}'.format(active_session, init_session))
    selected_runfile = [value for value in selected_runfile if value is not None]
    if not active_session:
        return [HIDE_STYLE] * 6
    # Default all to hide
    runfile_del, runfile_clone, session_del, session_new, detail_parameter, parameter_action = 6 * [HIDE_STYLE]
    if active_session == init_session:
        session_new = SHOW_STYLE
        if selected_rows:
            detail_parameter = SHOW_STYLE
            parameter_action = HIDE_STYLE
    else:
        session_del = SHOW_STYLE
        if selected_runfile:
            runfile_del, runfile_clone = [SHOW_STYLE] * 2
        if selected_rows:
            detail_parameter = SHOW_STYLE
            parameter_action = SHOW_STYLE

    return runfile_del, runfile_clone, session_del, session_new, detail_parameter, parameter_action


# Define fixed Output objects
fixed_outputs = [
    Output(Runfile.TABLE.value, 'data'),
]
fixed_states = [

    State(Runfile.TABLE.value, 'data'),

]
# Define dynamic Output objects based on a list of field names
field_names = table_column
dynamic_outputs = [Output(field, 'value', allow_duplicate=True) for field in field_names]
dynamic_states = [State(field, 'value') for field in field_names]
# Combine fixed and dynamic Output objects

all_outputs = fixed_outputs + dynamic_outputs
all_states = fixed_states + dynamic_states


# display selected row
@app.callback(
    dynamic_outputs,
    [
        Input(Runfile.TABLE.value, "selected_rows"),
        Input(Runfile.TABLE.value, 'data'),

    ],
    prevent_initial_call=True, )
def display_selected_row(selected_row, data):
    if not ctx.triggered:
        raise PreventUpdate
    print('triggered_id here', ctx.triggered_id)
    output_values = [''] * (len(table_column))
    if data:
        df = pd.DataFrame(data)
        df.fillna('', inplace=True)
        if selected_row:
            print('selected_row', selected_row, 'df len', len(df))
            if selected_row[0] < len(df):
                selected_data = df.loc[selected_row[0]]
                output_values = pf.table_layout([selected_data[col] for col in table_column])
    return output_values


# save the parameter to the runfile and dataTable

@app.callback(
    Output(Runfile.TABLE.value, 'data'),
    [
        Input(Table.DEL_ROW_BTN.value, 'n_clicks'),
        Input(Parameter.SAVE_ROW_BTN.value, 'n_clicks'),
        Input(Parameter.UPDATE_BTN.value, 'n_clicks'),
        Input(Runfile.TABLE.value, "selected_rows"),
        Input({'type': 'runfile-radio', 'index': ALL}, 'value'),
    ],
    all_states,
    prevent_initial_call=True,
)
def new_job(n1, n2, n3, selected_row, selected_runfile, df_table, *state_values):
    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]
    logger.info(f'Triggered component to update runfile: {triggered_id}')
    output_value = ''
    df = pd.DataFrame(df_table)
    print('slected row here', selected_row, 'selected_runfile here', selected_runfile)
    selected_runfile = [value for value in selected_runfile if value is not None]
    if selected_runfile:
        selected_runfile = selected_runfile[0]
        if selected_row:
            if triggered_id == Table.DEL_ROW_BTN.value:
                logger.info(f'Deleting row {selected_row[0]}')
                df.drop(df.index[selected_row[0]], inplace=True)
                pf.save_runfile(df, selected_runfile)
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
                pf.save_runfile(df, selected_runfile)
    output_value = df.to_dict('records')
    # logger.debug(f'Updated table values: {output_values}')
    return output_value


#
# @app.callback(
#     Output(Runfile.TABLE.value, 'selected_rows'),
#     Output(Runfile.TABLE.value, 'data',allow_duplicate=True),
#     Input({'type': 'runfile-radio', 'index': ALL}, 'value'),
#     State(Runfile.TABLE.value, 'data'),
#     prevent_initial_call=True)
# def clear_selected_row(selected_runfile, data):
#     if not ctx.triggered:
#         raise PreventUpdate
#     else:
#         triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]
#         print('print triggered_id', triggered_id)
#         if triggered_id.startswith('{"type": "runfile-radio","index'):
#             return [], data
#         else:
#             return no_update, data


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
