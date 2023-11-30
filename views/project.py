
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
        html.Div(dbc.Container(ui.session_layout)),
        html.Div(dbc.Container(ui.runfile_layout)),
        ui.parameter_layout
    ])


# Hide the Delete Session and Edit, delete, clone runfile for the default session
@app.callback(
    [
        Output(Runfile.DEL_BTN.value, 'style'),
        Output(Runfile.EDIT_BTN.value, 'style'),
        Output(Runfile.CLONE_BTN.value, 'style'),
        Output(Session.DEL_BTN.value, 'style'),
        Output(Session.NEW_BTN.value, 'style'),
    ],
    [
        Input(Session.SESSION_LIST.value, 'active_item'),
    ],

)
def default_session(active_session):
    logger.info('active_session: {}, init_session: {}'.format(active_session, init_session))
    # Default all to hide
    runfile_del, runfile_edit, runfile_clone, session_del, session_new = 5 * [SHOW_STYLE]
    if active_session is None:
        session_del, session_new = 2 * [HIDE_STYLE]
    elif active_session == init_session:
        session_del, runfile_edit, runfile_del, runfile_clone = [HIDE_STYLE] * 4
    return runfile_del, runfile_edit, runfile_clone, session_del, session_new


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
        Input(Runfile.SAVE_CLONE_RUNFILE_BTN.value, 'n_clicks'),
        Input(Session.SESSION_LIST.value, 'active_item'),

    ],
    [
        State(Session.NAME_INPUT.value, 'value')
    ],
)
def update_session_display(*args):
    n1, n2, n3, n4, n5, active_session, name = args
    logger.info(f'Updating the session list')
    triggered_id = ctx.triggered_id
    logger.debug(f'Triggered: {triggered_id}')

    if not pf.check_user_exists():
        logger.error('User is not authenticated')
        return no_update, no_update, "User is not authenticated"

    pid_path = os.path.join(default_work_lmt, current_user.username)
    os.makedirs(pid_path, exist_ok=True)

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
            old_session_path = default_session_path if active_session == init_session \
                else os.path.join(pid_path, active_session, 'lmtoy_run', f'lmtoy_{current_user.username}')
            shutil.copytree(old_session_path, new_session_path)
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
        time.sleep(0.5)

    session_list = pf.get_session_list(init_session, pid_path)
    return session_list, modal_open, message


# if click delete session button show the confirmation
@app.callback(
    Output(Session.CONFIRM_DEL.value, 'displayed'),
    Output(Session.CONFIRM_DEL.value, 'message'),
    Input(Session.DEL_BTN.value, 'n_clicks'),
    Input(Session.SESSION_LIST.value, 'active_item'),
)
def display_confirmation(n_clicks, active_item):
    if ctx.triggered_id == Session.DEL_BTN.value:
        return True, f'Are you sure you want to delete {active_item}?'
    return False, ''


# display selected runfile
@app.callback(
    [
        Output(Runfile.CONTENT_TITLE.value, 'children'),
        Output(Runfile.CONTENT_DISPLAY.value, 'style'),
        Output(Runfile.CONTENT.value, 'children'),
    ],
    [
        Input({'type': 'runfile-radio', 'index': ALL}, 'value'),
        Input(Runfile.CONFIRM_DEL_ALERT.value, 'submit_n_clicks'),
        Input(Table.NEW_ROW_BTN.value, 'n_clicks'),
        Input(Parameter.UPDATE_BTN.value, 'n_clicks'),
        Input(Table.DEL_ROW_BTN.value, 'n_clicks'),
    ],
)
def display_runfile_content(selected_runfile, del_runfile_btn, n1, n2, n3):
    if not ctx.triggered:
        raise PreventUpdate
    current_runfile = next((value for value in selected_runfile if value), None)
    if not current_runfile:
        return '', HIDE_STYLE, ''

    runfile_title = pf.get_runfile_title(current_runfile, init_session)
    runfile_content = pf.df_runfile(current_runfile)[1]

    if ctx.triggered_id == Runfile.CONFIRM_DEL_ALERT.value:
        pf.del_runfile(current_runfile)
    if ctx.triggered_id in [Table.NEW_ROW_BTN.value, Parameter.UPDATE_BTN.value, Table.DEL_ROW_BTN.value]:
        time.sleep(0.5)
        runfile_content = pf.df_runfile(current_runfile)[1]
    logger.info(f'current_runfile is {current_runfile}')
    return runfile_title, SHOW_STYLE, runfile_content


# If edit was clicked, show the modal
@app.callback(

    Output(Parameter.MODAL.value, 'is_open'),
    Output(Runfile.TABLE.value, 'data', allow_duplicate=True),

    [
        Input(Runfile.EDIT_BTN.value, 'n_clicks'),
        Input({'type': 'runfile-radio', 'index': ALL}, 'value'),
    ],
)
def show_parameter_table(n1, selected_runfile):
    modal_style = False
    dff = pd.DataFrame(columns=table_column)
    if not ctx.triggered:
        raise PreventUpdate
    if ctx.triggered_id == Runfile.EDIT_BTN.value:  # If edit was clicked, show the modal
        modal_style = True
        current_runfile = next((value for value in selected_runfile if value), None)
        df = pf.df_runfile(current_runfile)[0]
        dff = pd.concat([df, dff])
    return modal_style, dff.to_dict('records')


fixed_states = [

    State(Runfile.TABLE.value, 'data'),

]
# Define dynamic Output objects based on a list of field names
field_names = table_column
dynamic_outputs = [Output(field, 'value', allow_duplicate=True) for field in field_names]
dynamic_states = [State(field, 'value') for field in field_names]
# Combine fixed and dynamic Output objects

all_states = fixed_states + dynamic_states


# save the parameter to the dataTable

@app.callback(
    Output(Runfile.TABLE.value, 'data'),
    [
        Input(Table.DEL_ROW_BTN.value, 'n_clicks'),
        Input(Table.NEW_ROW_BTN.value, 'n_clicks'),
        Input(Parameter.UPDATE_BTN.value, 'n_clicks'),
        Input({'type': 'runfile-radio', 'index': ALL}, 'value'),
    ],
    all_states,
    prevent_initial_call=True,
)
def save_new_parameters(n1, n2, n3, selected_runfile, df_table, *state_values):
    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]
    logger.info(f'Triggered component to update runfile: {triggered_id}')
    df = pd.DataFrame(df_table)
    selected_runfile = next((value for value in selected_runfile if value), None)
    if not selected_runfile:
        return no_update

    if triggered_id == Parameter.UPDATE_BTN.value:
        # update the table value of slected obsnums using parameter value
        obsumns = list(state_values[1])
        # change the value of rows which has the obsnum(s) in the obsumns
        parameter_values = state_values[2:]
        for obsumn in obsumns:
            for i, column in enumerate(table_column[2:]):
                value = parameter_values[i]
                if value is not None:
                    if i == 1:
                        print('value before sorted', value)
                        filtered_beam = filter(bool, value)
                        sorted_beam = sorted(filtered_beam, key=int)
                        value = ",".join(sorted_beam)
                        print('value after sorted', value)
                    elif i == 2:
                        value = f'[{value} ]'
                    df.loc[df[table_column[1]] == obsumn, column] = value
        pf.save_runfile(df, selected_runfile)
    output_value = df.to_dict('records')

    # logger.debug(f'Updated table values: {output_values}')
    return output_value


# if click delete button show the confirmation
@app.callback(
    Output(Runfile.CONFIRM_DEL_ALERT.value, 'displayed'),
    Output(Runfile.CONFIRM_DEL_ALERT.value, 'message'),
    [
        Input(Runfile.DEL_BTN.value, 'n_clicks'),
        Input({'type': 'runfile-radio', 'index': ALL}, 'value')
    ],
    prevent_initial_call=True
)
def display_confirmation(n_clicks, selected_runfile):
    selected_runfile = [value for value in selected_runfile if value is not None]

    if ctx.triggered_id == Runfile.DEL_BTN.value:
        if selected_runfile:
            file_name = selected_runfile[0].split('/')[-1]
            return True, f'Are you sure you want to delete {file_name}?'
        else:
            return False, ''
    else:
        return False, ''


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
        Input({'type': 'runfile-radio', 'index': ALL}, 'value'),
    ],
    [
        State(Runfile.NAME_INPUT.value, 'value'),
    ],

    prevent_initial_call=True
)
def copy_runfile(n1, n2, selected_runfile, new_name):
    if not ctx.triggered:
        raise PreventUpdate
    current_runfile = next((value for value in selected_runfile if value), None)
    modal_open = False
    status = False
    message = ''
    triggered_id = ctx.triggered_id
    if triggered_id == Runfile.CLONE_BTN.value:
        modal_open = True
    if triggered_id == Runfile.SAVE_CLONE_RUNFILE_BTN.value:
        new_runfile_name = f"{current_user.username}.{new_name}"
        pf.clone_runfile(current_runfile, new_runfile_name)
        message = f'Runfile {new_runfile_name} saved successfully!'
    return modal_open, message, status


# when selected_rows is not none, show the edit row button and delete row button
@app.callback(
    Output(Table.OPTION.value, 'style'),
    Input(Runfile.TABLE.value, "selected_rows"),
    Input(Parameter.DETAIL.value, 'style'),
)
def show_edit_row_btn(selected_rows, style):
    if selected_rows and style == HIDE_STYLE:
        return SHOW_STYLE
    else:
        return HIDE_STYLE


# if edit selected row button or new row btn is clicked, show the parameter detail layout
@app.callback(
    Output(Parameter.DETAIL.value, 'style'),
    Input(Table.EDIT_TABLE.value, 'n_clicks'),
    Input(Parameter.UPDATE_BTN.value, 'n_clicks'),
    Input(Table.NEW_ROW_BTN.value, 'n_clicks'),
    Input(Table.CONFIRM_DEL_ROW.value, 'submit_n_clicks'),
    Input(Runfile.TABLE.value, "selected_rows"),
    Input(Parameter.CANCEL_BTN.value, 'n_clicks'),
)
def show_parameter_detail(n1, n2, n3, n4, selected_rows, n5):
    print('selected_rows', selected_rows)
    if not ctx.triggered:
        raise PreventUpdate
    if not selected_rows:
        return HIDE_STYLE
    elif ctx.triggered_id == Table.EDIT_TABLE.value:
        return SHOW_STYLE
    elif (ctx.triggered_id == Parameter.UPDATE_BTN.value or ctx.triggered_id == Table.CONFIRM_DEL_ROW.value
          or ctx.triggered_id == Parameter.CANCEL_BTN.value):
        return HIDE_STYLE
    else:
        return no_update


# if delete row button is clicked, show the confirmation to delete the row
@app.callback(
    Output(Table.CONFIRM_DEL_ROW.value, 'displayed'),
    Output(Table.CONFIRM_DEL_ROW.value, 'message'),
    Input(Table.DEL_ROW_BTN.value, 'n_clicks'),
    # State(Runfile.TABLE.value, "selected_rows"),
    prevent_initial_call=True
)
def display_confirmation(n_clicks):
    if ctx.triggered_id == Table.DEL_ROW_BTN.value:
        return True, 'Are you sure you want to delete the selected row(s)?'
    return False, ''


# if table.confirm_del_row is clicked delete the selected row
# if table.new_row_btn is clicked add selected rows to the table
# @app.callback(
#     Output(Runfile.TABLE.value, 'data', allow_duplicate=True),
#     Input(Table.CONFIRM_DEL_ROW.value, 'submit_n_clicks'),
#     Input(Table.NEW_ROW_BTN.value, 'n_clicks'),
#     Input({'type': 'runfile-radio', 'index': ALL}, 'value'),
#     State(Runfile.TABLE.value, 'data'),
#     State(Runfile.TABLE.value, "selected_rows"),
#     prevent_initial_call=True
# )
# def delete_add_row(n1, n2, selected_runfile, df_table, selected_rows):
#     if not ctx.triggered:
#         raise PreventUpdate
#
#     selected_runfile = next((value for value in selected_runfile if value), None)
#     df = pd.DataFrame(df_table)
#     if selected_rows:
#         selected_rows = [value for value in selected_rows if value is not None]
#         if ctx.triggered_id == Table.CONFIRM_DEL_ROW.value:
#             selected_rows.sort(reverse=True)
#             for row in selected_rows:
#                 df.drop(row, inplace=True)
#             pf.save_runfile(df, selected_runfile)
#             output_value = df.to_dict('records')
#             return output_value
#         elif ctx.triggered_id == Table.NEW_ROW_BTN.value:
#             for row in selected_rows:
#                 new_row = df.loc[row]
#                 df = df._append(new_row, ignore_index=True)
#             output_value = df.to_dict('records')
#             return output_value
#
#     else:
#         return no_update

import pandas as pd
from dash import callback_context as ctx
from dash.exceptions import PreventUpdate


# Assuming other necessary imports and initializations

@app.callback(
    Output(Runfile.TABLE.value, 'data', allow_duplicate=True),
    [Input(Table.CONFIRM_DEL_ROW.value, 'submit_n_clicks'),
     Input(Table.NEW_ROW_BTN.value, 'n_clicks'),
     Input({'type': 'runfile-radio', 'index': ALL}, 'value')],
    [State(Runfile.TABLE.value, 'data'),
     State(Runfile.TABLE.value, "selected_rows")],
    prevent_initial_call=True
)
def delete_add_row(n1, n2, selected_runfile, df_table, selected_rows):
    if not ctx.triggered:
        raise PreventUpdate

    selected_runfile = next((value for value in selected_runfile if value), None)
    df = pd.DataFrame(df_table)

    if selected_rows:
        selected_rows = [value for value in selected_rows if value is not None]

        if ctx.triggered_id == Table.CONFIRM_DEL_ROW.value:
            # Delete selected rows
            selected_rows.sort(reverse=True)
            for row in selected_rows:
                if row in df.index:
                    df.drop(row, inplace=True)
            pf.save_runfile(df, selected_runfile)
            return df.to_dict('records')

        elif ctx.triggered_id == Table.NEW_ROW_BTN.value:
            # Add new rows
            for row in selected_rows:
                if row in df.index:
                    new_row = df.loc[row]
                    df = df._append(new_row, ignore_index=True)
            pf.save_runfile(df, selected_runfile)
            return df.to_dict('records')

    return no_update


@app.callback(
    Output(table_column[1], 'value'),
    Output(table_column[0], 'value'),
    Input(Runfile.TABLE.value, "selected_rows"),
    State(Runfile.TABLE.value, 'data'),
)
def update_dropdown_from_table(selected_row, data):
    if not selected_row or not data:
        return no_update

    df = pd.DataFrame(data)
    obsnum_values = [df.loc[row][table_column[1]] for row in selected_row]
    source_value = df.loc[selected_row[0]][table_column[0]]
    return obsnum_values, source_value


# if value in obsnum is changed, update the table selected_rows
@app.callback(
    Output(Runfile.TABLE.value, "selected_rows"),
    Input(table_column[1], 'value'),
    State(Runfile.TABLE.value, 'data'),
    prevent_initial_call=True,
)
def update_selected_row(obsnum_values, data):
    if not ctx.triggered:
        raise PreventUpdate
    if data:
        df = pd.DataFrame(data)
        selected_rows = []
        for obsnum in obsnum_values:
            selected_rows.append(df[df[table_column[1]] == obsnum].index[0])
        return selected_rows
    return no_update


# if new row button selected, show the detail parameter layout and append the value to the end of table

# if login get the options for source and obsnums
@app.callback(
    [
        Output(Parameter.SOURCE_DROPDOWN.value, 'options'),
        Output(Storage.DATA_STORE.value, 'data'),
    ],
    [
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


#
#
# verify the selected_runfile
@app.callback(
    Output(Runfile.VALIDATION_ALERT.value, 'is_open'),
    Output(Runfile.VALIDATION_ALERT.value, 'children'),
    Input(Runfile.RUN_BTN.value, 'n_clicks'),
    State({'type': 'runfile-radio', 'index': ALL}, 'value'),
)
def verify_runfile(n_clicks, selected_runfile):
    if not ctx.triggered:
        raise PreventUpdate
    selected_runfile = [value for value in selected_runfile if value is not None]
    if selected_runfile:
        selected_runfile = selected_runfile[0]
        logger.info(f'Verifying runfile: {selected_runfile}')
        message = runs.verify(selected_runfile, debug=False)
        if message:
            show_message = 'Runfile verification failed: ' + message
        else:
            show_message = 'Runfile verification passed!'
        return True, show_message
    else:
        return False, ''


app.clientside_callback(
    """
    function(n_clicks) {
        if (n_clicks > 0) {
            var element = document.getElementById('runfile-end');
            if (element) {
                element.scrollIntoView({behavior: 'smooth'});
            }
        }
    }
    """,
    Output('dummy-div', 'children'),  # Dummy output
    Input(Runfile.EDIT_BTN.value, 'n_clicks'),
)
