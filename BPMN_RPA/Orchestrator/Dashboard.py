import base64
import datetime
import json
import multiprocessing
import os
import sqlite3
import subprocess
import winreg
from datetime import date
from datetime import datetime
from os import listdir
from os.path import isfile, join
from typing import Any

import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import pandas as pd
from dash.dependencies import Input, Output, State
from dateutil.utils import today

# region Functions and globals
from BPMN_RPA.WorkflowEngine import WorkflowEngine, SQL


# region Global functions and style

def flow_runner(flowfile):
    """
    Run a flow from file
    :param flowfile: The full path to the floe file.
    """
    engine = WorkflowEngine()
    doc = engine.open(flowfile)
    steps = engine.get_flow(doc)
    engine.run_flow(steps)


def get_reg(name):
    try:
        REG_PATH = r"SOFTWARE\BPMN_RPA"
        registry_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_PATH, 0, winreg.KEY_READ)
        value, regtype = winreg.QueryValueEx(registry_key, name)
        winreg.CloseKey(registry_key)
        return value
    except WindowsError:
        return None


def add_images_to_dataframe(df: Any, columnName: str = "status") -> Any:
    """
    Add the image urls as markup to the Pandas dataframe object
    :param df: The Pandas dataframe object
    :param columnName: The name of the column to add the images to
    :return: Changed Pandas dataframe object
    """
    t = 0
    for row in df.iterrows():
        if str(df.at[t, "result"]).startswith("Error"):
            df.at[
                t, columnName] = "![ok](https://raw.githubusercontent.com/joostvangils/BPMN_RPA/main/BPMN_RPA/Images/error.png)"
        else:
            df.at[
                t, columnName] = "![ok](https://raw.githubusercontent.com/joostvangils/BPMN_RPA/main/BPMN_RPA/Images/ok.png)"
        t += 1
    return df


def get_columns_with_image_from_dataframe(df: Any, columnName: str = "status") -> Any:
    """
    Get the Column collection of the Pandas dataframe with the specific presentation for the Status column
    :param df: The Pandas dataframe object
    :param columnName: The name of the column that needs to be formatted to hold an image
    :return: Column collection
    """
    columns = [{"name": i, "id": i} for i in df.columns]
    imagecolumn = [element for element in columns if element['name'] == columnName][0]
    imagecolumn["presentation"] = "markdown"
    imagecolumn["editable"] = False
    return columns


buttonstyle = {'box-shadow': 'inset 0px 1px 0px 0px #54a3f7',
               'background': 'linear-gradient(to bottom, #007dc1 5%, #0061a7 100%)',
               'background-color': '#007dc1',
               'border-radius': '3px',
               'border': '1px solid #124d77',
               'display': 'inline-block',
               'cursor': 'pointer',
               'color': '#ffffff',
               'font-family': 'Verdana',
               'font-size': '13px',
               'margin': '2px',
               'padding': '6px 24px',
               'text-decoration': 'none',
               'text-shadow': '0px 1px 0px #154682',
               }

# region Universal header
universal_header = html.Table(id="header", style={'margin': '0', 'padding': '0', 'width': '100%'}, children=[
    html.Tr(children=[
        html.Td(children=[
            html.Img(
                src="https://raw.githubusercontent.com/joostvangils/BPMN_RPA/main/BPMN_RPA/Images/BPMN_RPA_logo.PNG",
                width="280px", height="55px", style={'float': 'left'}),

        ]),
        html.Td(children=[
            html.H2("Orchestrator", style={'font-family': 'Verdana', 'margin': '4px'}),

        ], style={'text-align': 'left'}),
        html.Td(children=[
            html.A(html.Button('Overview', className='menu_main', style=buttonstyle), href='/main_page'),
            html.A(html.Button('Run', className='menu_main', style=buttonstyle), href='/run_page'),
        ]),
    ]),
])
# endregion

# endregion

app = dash.Dash(__name__)

# region SQLite content
server = app.server
dbpath = get_reg('dbPath')
connection = sqlite3.connect(rf'{dbpath}\orchestrator.db')

# Check if tables exist, otherwise create them
sql = SQL(dbpath)
sql.orchestrator()

# Check registered flows and remove from directory if not in database
registered_in_db = sql.get_registered_flows()
files_in_dir = [f for f in listdir(f"{dbpath}\\Registered Flows") if isfile(join(f"{dbpath}\\Registered Flows", f))]
for file_in_dir in files_in_dir:
    if file_in_dir not in registered_in_db:
        os.remove(f"{dbpath}\\Registered Flows\\{file_in_dir}")
rm = []
for file_in_db in registered_in_db:
    if file_in_db not in files_in_dir:
        rm.append(file_in_db)
if len(rm) > 0:
    sql.remove_registered_flows(rm)

# Prepare datatable queries
sql = "Select id, name, description from Registered"
registered_flows = pd.read_sql_query(sql, connection)
registered_flows_columns = [{"name": i, "id": i} for i in registered_flows.columns]
decsription_column = [x for x in registered_flows_columns if x["id"] == "description"][0]
decsription_column.update({'editable': True})

sql = "Select * from Triggers"
triggers = pd.read_sql_query(sql, connection)
triggers_columns = [{"name": i, "id": i} for i in triggers.columns]

sql = f"SELECT id, name, result, started, finished FROM Workflows ORDER BY finished DESC;"
flows = pd.read_sql_query(sql, connection)
flows = add_images_to_dataframe(flows, "result")
flows_columns = get_columns_with_image_from_dataframe(flows, "result")

sql = f"SELECT id, workflow, name, status, step, result, timestamp as executed FROM Steps ORDER BY id DESC;"
steps = pd.read_sql_query(sql, connection)
steps = add_images_to_dataframe(steps)
step_columns = get_columns_with_image_from_dataframe(steps)
workflow_column = [x for x in step_columns if x["id"] == "workflow"][0]
workflow_column.update({'hideable': True})
# endregion

app = dash.Dash(name="BPMN RPA", title="BPMN RPA")
app.config.suppress_callback_exceptions = True

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

# region MainPage
mainpage_layout = html.Div([
    # Header
    html.Span([
        dcc.Interval(
            id='interval-component',
            interval=1*5000,  # in milliseconds
            n_intervals=0
        ),
        universal_header,
        html.Tr(children=[
            html.Td(children=[
                html.H4("Executed flows", style={'font-family': 'Verdana', 'margin': '4px'}),
            ]),
        ]),
    ]),
    # region datatables
    dash_table.DataTable(
        id='flows',
        columns=flows_columns,
        editable=False,
        data=flows.to_dict('records'),
        sort_action='native',
        filter_action='native',
        style_cell={'textAlign': 'left', 'overflow': 'visible', 'textOverflow': 'ellipsis', 'height': '40px',
                    'font-family': 'Verdana', 'font-size': '12px',
                    'selector': 'td.cell--selected, td.focused', 'rule': 'background-color: #FF4136;'},
        style_header={'backgroundColor': 'rgb(0, 0, 153)', 'font-family': 'Verdana', 'fontWeight': 'bold',
                      'color': 'white', 'overflow': 'hidden', 'textOverflow': 'ellipsis'},
        style_data_conditional=[{'if': {'row_index': 'odd'}, 'backgroundColor': 'rgb(248, 248, 248)'},
                                {'if': {'state': 'selected'}, 'backgroundColor': 'rgba(0, 116, 217, 0.3)',
                                 'border': '1px rgba(0, 116, 217, 0.3)'},
                                ],
        # {'if': {'column_id': 'status', 'filter_query': '{result} eq "True"'}, 'width': '50%'}],
        # style_header_conditional=[{'if': {'column_id': 'status'}, 'fontSize': '15px'}],
        page_action="native",
        page_current=0,
        page_size=5,
        selected_columns=[],
    ),
    html.Br(),
    html.H4("Executed steps", style={'font-family': 'Verdana', 'margin': '4px'}),
    dash_table.DataTable(
        id='steps',
        columns=step_columns,
        hidden_columns=['workflow'],
        editable=False,
        data=steps.to_dict('records'),
        sort_action='native',
        filter_action='native',
        style_cell={'textAlign': 'left', 'overflow': 'visible', 'textOverflow': 'ellipsis', 'height': '40px',
                    'font-family': 'Verdana', 'font-size': '12px'},
        style_header={'backgroundColor': 'rgb(0, 0, 153)', 'font-family': 'Verdana', 'fontWeight': 'bold',
                      'color': 'white', 'overflow': 'hidden', 'textOverflow': 'ellipsis'},
        style_data_conditional=[{'if': {'row_index': 'odd'}, 'backgroundColor': 'rgb(248, 248, 248)'},
                                {'if': {'state': 'selected'}, 'backgroundColor': 'rgba(0, 116, 217, 0.3)',
                                 'border': '1px rgba(0, 116, 217, 0.3)'},
                                ],
        # {'if': {'column_id': 'status', 'filter_query': '{result} eq "True"'}, 'width': '50%'}],
        style_cell_conditional=[{'if': {'column_id': 'started'}}],
        # style_header_conditional=[{'if': {'column_id': 'status'}, 'fontSize': '15px'}],
        page_action="native",
        page_current=0,
        page_size=10,

    ),
    dcc.Input(id='empty_refresh', value='0', type='text', style={'display': 'none'}),
    # endregion
])


# endregion

# region CallBack functions main page

@app.callback(
    [Output('flows', 'data'), Output('empty_refresh', 'value')],
    Input('interval-component', 'n_intervals')
)
def refreshdata(n_intervals):
    connection = sqlite3.connect(rf'{dbpath}\orchestrator.db')
    sql_ = f"SELECT id, name, result, started, finished FROM Workflows ORDER BY finished DESC;"
    flows_ = pd.read_sql_query(sql_, connection)
    flows_ = add_images_to_dataframe(flows_, "result")
    return flows_.to_dict('records'), n_intervals


@app.callback(
    [Output('flows', 'style_data_conditional'), Output('steps', 'data')],
    [Input('flows', 'active_cell'), Input('empty_refresh', 'value')]
)
def select_row_filter_data(active_cell, empty_refresh):
    connection = sqlite3.connect(rf'{dbpath}\orchestrator.db')
    if active_cell is not None:
        style = [{'if': {'row_index': 'odd'}, 'backgroundColor': 'rgb(248, 248, 248)'},
                 {'if': {'row_index': active_cell["row"]}, 'backgroundColor': 'rgba(0, 116, 217, 0.3)'},
                 {'if': {'state': 'selected'}, 'backgroundColor': 'rgba(0, 116, 217, 0.3)',
                  'border': '1px rgba(0, 116, 217, 0.3)'}, ]
        sql = f"SELECT id, workflow, name, status, step, result, timestamp as executed FROM Steps WHERE workflow = {active_cell['row_id']} ORDER BY id DESC ;"
        steps = pd.read_sql_query(sql, connection)
        steps = add_images_to_dataframe(steps)
    else:
        style = [{'if': {'row_index': 'odd'}, 'backgroundColor': 'rgb(248, 248, 248)'},
                 {'if': {'state': 'selected'}, 'backgroundColor': 'rgba(0, 116, 217, 0.3)',
                  'border': '1px rgba(0, 116, 217, 0.3)'}, ]
        sql = f"SELECT id, workflow, name, status, step, result, timestamp as executed FROM Steps ORDER BY id DESC;"
        steps = pd.read_sql_query(sql, connection)
        steps = add_images_to_dataframe(steps)
    return style, steps.to_dict('records')


# endregion

# region Run page
runpage_layout = html.Div([
    # Header
    html.Span([
        universal_header,
        html.Tr(children=[
            html.Td(children=[
                html.H4("Registered flows", style={'font-family': 'Verdana', 'margin': '4px'}),
            ]),
        ]),
    ]),
    html.Table([
        html.Tr([
            # Registered datatable
            html.Td(children=[
                dash_table.DataTable(
                    id='registered',
                    columns=registered_flows_columns,
                    editable=False,
                    data=registered_flows.to_dict('records'),
                    sort_action='native',
                    filter_action='native',
                    style_table={'min-width': '300px'},
                    style_cell={'textAlign': 'left', 'overflow': 'visible', 'textOverflow': 'ellipsis',
                                'height': '40px', 'font-family': 'Verdana', 'font-size': '12px'},
                    style_header={'backgroundColor': 'rgb(0, 0, 153)', 'font-family': 'Verdana', 'fontWeight': 'bold',
                                  'color': 'white', 'overflow': 'hidden', 'textOverflow': 'ellipsis'},
                    style_data_conditional=[{'if': {'row_index': 'odd'}, 'backgroundColor': 'rgb(248, 248, 248)'},
                                            {'if': {'state': 'selected'}, 'backgroundColor': 'rgba(0, 116, 217, 0.3)',
                                             'border': '1px rgba(0, 116, 217, 0.3)'},
                                            ],
                    # {'if': {'column_id': 'status', 'filter_query': '{result} eq "True"'}, 'width': '50%'}],
                    # style_cell_conditional=[{'if': {'column_id': 'description'}, 'editable': True}],
                    # style_header_conditional=[{'if': {'column_id': 'status'}, 'fontSize': '15px'}],
                    page_action="native",
                    page_current=0,
                    page_size=7,

                )
            ], style={'vertical-align': 'top'}),
            # Register flow and flow operations
            html.Td([
                html.Table(children=[
                    html.Tr(children=[
                        html.Th(children=["Register Flows"],
                                style={'backgroundColor': 'rgb(0, 0, 153)', 'font-family': 'Verdana',
                                       'font-size': '15px', 'height': '38px', 'width': '300px', 'fontWeight': 'bold',
                                       'color': 'white', 'overflow': 'hidden', 'textOverflow': 'ellipsis'})
                    ]),
                    html.Tr(children=[
                        html.Td([
                            html.Div([
                                dcc.Upload(
                                    id='datatable-upload',
                                    children=html.Div([
                                        'Drag and Drop or ',
                                        html.A('Select Flow-files to register')
                                    ]),
                                    style={
                                        'width': '100%', 'height': '60px', 'lineHeight': '60px',
                                        'borderWidth': '1px', 'borderStyle': 'dashed', 'font-size': '12px',
                                        'font-family': 'Verdana',
                                        'borderRadius': '5px', 'textAlign': 'center'},
                                ),
                                dash_table.DataTable(id='datatable-upload-container'),
                            ])
                        ]),
                    ]),
                ], style={'margin-top': '-1px'}),
                html.Table(children=[
                    html.Tr(children=[
                        html.Th(children=["Flow operations"],
                                style={'backgroundColor': 'rgb(0, 0, 153)', 'font-family': 'Verdana',
                                       'font-size': '15px', 'height': '38px', 'width': '300px', 'fontWeight': 'bold',
                                       'color': 'white', 'overflow': 'hidden', 'textOverflow': 'ellipsis'})
                    ]),
                    html.Tr(children=[
                        html.Td(children=[
                            html.Button(id='delete_button', children=[
                                html.Span([
                                    html.Img(
                                        src='https://raw.githubusercontent.com/joostvangils/BPMN_RPA/main/BPMN_RPA/Images/delete.png',
                                        style={'width': '25px'})
                                ])
                            ], style={'background-color': 'Transparent', 'border': 'none', 'cursor': 'pointer'}),
                            html.Div(id='empty_delete', children=[], style={'display': 'none'}),
                            html.Button(id='edit_button', children=[
                                html.Span([
                                    html.Img(
                                        src='https://raw.githubusercontent.com/joostvangils/BPMN_RPA/main/BPMN_RPA/Images/edit.png',
                                        style={'width': '25px'})
                                ])
                            ], style={'background-color': 'Transparent', 'border': 'none', 'cursor': 'pointer'}),
                            html.Div(id='empty_edit', children=[], style={'display': 'none'}),
                            html.Button(id='run_button', children=[
                                html.Span([
                                    html.Img(
                                        src='https://raw.githubusercontent.com/joostvangils/BPMN_RPA/main/BPMN_RPA/Images/run.png',
                                        style={'width': '25px'})
                                ])
                            ], style={'background-color': 'Transparent', 'border': 'none', 'cursor': 'pointer'}),
                            html.Div(id='selected_row', children=[], style={'display': 'none'}),
                            html.Div(id='empty_run', children=[], style={'display': 'none'}),
                            html.Div(id='to_do', children=[], style={'display': 'none'}),
                            html.Div(id='yes_no', children=[], style={'display': 'none'}),
                        ], style={'border': '1px solid #d9d9d9'}),
                    ]),
                ])
            ]),
            # Scheduler
            html.Td([
                html.Table(children=[
                    # Header Scheduler
                    html.Tr(children=[
                        html.Th(children=["Schedule"],
                                style={'backgroundColor': 'rgb(0, 0, 153)', 'font-family': 'Verdana',
                                       'font-size': '15px', 'height': '36px', 'width': '300px', 'fontWeight': 'bold',
                                       'color': 'white', 'overflow': 'hidden', 'textOverflow': 'ellipsis'})
                    ]),
                    # Fire trigger
                    html.Tr(children=[
                        html.Td(children=[
                            html.Label("Fire trigger", style={'font-family': 'Verdana'})
                        ]),
                    ]),
                    html.Tr(children=[
                        html.Td(children=[
                            dcc.Dropdown(
                                id='fire_trigger', style={'font-family': 'Verdana', 'font-size': '12px'},
                                options=[
                                    {'label': 'Daily', 'value': 'daily'},
                                    {'label': 'On specific dates', 'value': 'specific_dates'},
                                    {'label': 'Weekly', 'value': 'weekly'},
                                    {'label': 'Monthly', 'value': 'monthly'}
                                ],
                                value='Daily'
                            ),
                        ]),
                    ]),
                    # Specific dates datepicker
                    html.Tr(id="specific_dates", style={'text-align': 'center', 'display': 'table-row'}, children=[
                        html.Label("Trigger date", style={'font-family': 'Verdana'}),
                        html.Br(),
                        dcc.DatePickerSingle(
                            id='specific_date',
                            initial_visible_month=date(today().year, today().month, today().day),
                            display_format='DD-MM-YYYY',
                            date=date(today().year, today().month, today().day),
                            style={'font-family': 'Verdana', 'font-size': '12px'}
                        ),
                        html.Br(),
                    ]),
                    # Weekly
                    html.Tr(id="weekly", style={'text-align': 'center', 'display': 'table-row'}, children=[
                        html.Br(),
                        html.Label("Weekly on", style={'font-family': 'Verdana'}),
                        html.Br(),
                        dcc.Checklist(id='weekly_checklist',
                                      options=[
                                          {'label': 'Monday', 'value': 'monday'},
                                          {'label': 'Tuesday', 'value': 'tuesday'},
                                          {'label': 'Wednesday', 'value': 'wednesday'},
                                          {'label': 'Thursday', 'value': 'thursday'},
                                          {'label': 'Friday', 'value': 'friday'},
                                          {'label': 'Saturday', 'value': 'saturday'},
                                          {'label': 'Sunday', 'value': 'sunday'},
                                      ]
                                      ),
                        html.Br(),
                    ]),
                    # Monthly
                    html.Tr(id="monthly", style={'text-align': 'center', 'display': 'none'}, children=[
                        html.Br(),
                        html.Label("Days", style={'font-family': 'Verdana'}),
                        html.Br(),
                        dcc.Checklist(id='monthly_days',
                                      options=[
                                          {'label': '1', 'value': '1'},
                                          {'label': '2', 'value': '2'},
                                          {'label': '3', 'value': '3'},
                                          {'label': '4', 'value': '4'},
                                          {'label': '5', 'value': '5'},
                                          {'label': '6', 'value': '6'},
                                          {'label': '7', 'value': '7'},
                                          {'label': '8', 'value': '8'},
                                          {'label': '9', 'value': '9'},
                                          {'label': '10', 'value': '10'},
                                          {'label': '11', 'value': '11'},
                                          {'label': '12', 'value': '12'},
                                          {'label': '13', 'value': '13'},
                                          {'label': '14', 'value': '14'},
                                          {'label': '15', 'value': '15'},
                                          {'label': '16', 'value': '16'},
                                          {'label': '17', 'value': '17'},
                                          {'label': '18', 'value': '18'},
                                          {'label': '19', 'value': '19'},
                                          {'label': '20', 'value': '20'},
                                          {'label': '21', 'value': '21'},
                                          {'label': '22', 'value': '22'},
                                          {'label': '23', 'value': '23'},
                                          {'label': '24', 'value': '24'},
                                          {'label': '25', 'value': '25'},
                                          {'label': '26', 'value': '26'},
                                          {'label': '27', 'value': '27'},
                                          {'label': '28', 'value': '28'},
                                          {'label': '29', 'value': '29'},
                                          {'label': '30', 'value': '30'},
                                          {'label': '31', 'value': '31'},
                                          {'label': 'Last day of month', 'value': 'last_day'},
                                          {'label': 'Last working day of month', 'value': 'last_working_day'},
                                      ],
                                      ),
                        html.Br(),
                        html.Label("Months", style={'font-family': 'Verdana'}),
                        html.Br(),
                        dcc.Checklist(id='monthly_months',
                                      options=[
                                          {'label': 'January', 'value': 'january'},
                                          {'label': 'February', 'value': 'february'},
                                          {'label': 'March', 'value': 'march'},
                                          {'label': 'April', 'value': 'april'},
                                          {'label': 'May', 'value': 'may'},
                                          {'label': 'June', 'value': 'june'},
                                          {'label': 'July', 'value': 'july'},
                                          {'label': 'August', 'value': 'august'},
                                          {'label': 'September', 'value': 'september'},
                                          {'label': 'October', 'value': 'october'},
                                          {'label': 'November', 'value': 'november'},
                                          {'label': 'December', 'value': 'december'},

                                      ],
                                      value=['january', 'february', 'march', 'april', 'may', 'june', 'july', 'august',
                                             'september', 'october', 'november', 'december'],
                                      ),
                        html.Br(),
                    ]),
                    # Add time
                    html.Tr(id="daily", children=[
                        html.Td(children=[
                            html.Label("Trigger time", style={'font-family': 'Verdana'}),
                            html.Br(),
                            # time setter
                            html.Label("Hour", style={'font-family': 'Verdana', 'font-size': '12px'}),
                            dcc.Dropdown(
                                id='hour', style={'font-family': 'Verdana', 'font-size': '12px'},
                                options=[
                                    {'label': '01', 'value': '01'},
                                    {'label': '02', 'value': '02'},
                                    {'label': '03', 'value': '03'},
                                    {'label': '04', 'value': '04'},
                                    {'label': '05', 'value': '05'},
                                    {'label': '06', 'value': '06'},
                                    {'label': '07', 'value': '07'},
                                    {'label': '08', 'value': '08'},
                                    {'label': '09', 'value': '09'},
                                    {'label': '10', 'value': '10'},
                                    {'label': '11', 'value': '11'},
                                    {'label': '12', 'value': '12'},
                                    {'label': '13', 'value': '13'},
                                    {'label': '14', 'value': '14'},
                                    {'label': '15', 'value': '15'},
                                    {'label': '16', 'value': '16'},
                                    {'label': '17', 'value': '17'},
                                    {'label': '18', 'value': '18'},
                                    {'label': '19', 'value': '19'},
                                    {'label': '20', 'value': '20'},
                                    {'label': '21', 'value': '21'},
                                    {'label': '22', 'value': '22'},
                                    {'label': '23', 'value': '23'},
                                    {'label': '24', 'value': '24'},
                                ]),
                            html.Label("Minute", style={'font-family': 'Verdana', 'font-size': '12px'}),
                            dcc.Dropdown(
                                id='minute', style={'font-family': 'Verdana', 'font-size': '12px'},
                                options=[
                                    {'label': '01', 'value': '01'},
                                    {'label': '02', 'value': '02'},
                                    {'label': '03', 'value': '03'},
                                    {'label': '04', 'value': '04'},
                                    {'label': '05', 'value': '05'},
                                    {'label': '06', 'value': '06'},
                                    {'label': '07', 'value': '07'},
                                    {'label': '08', 'value': '08'},
                                    {'label': '09', 'value': '09'},
                                    {'label': '10', 'value': '10'},
                                    {'label': '11', 'value': '11'},
                                    {'label': '12', 'value': '12'},
                                    {'label': '13', 'value': '13'},
                                    {'label': '14', 'value': '14'},
                                    {'label': '15', 'value': '15'},
                                    {'label': '16', 'value': '16'},
                                    {'label': '17', 'value': '17'},
                                    {'label': '18', 'value': '18'},
                                    {'label': '19', 'value': '19'},
                                    {'label': '20', 'value': '20'},
                                    {'label': '21', 'value': '21'},
                                    {'label': '22', 'value': '22'},
                                    {'label': '23', 'value': '23'},
                                    {'label': '24', 'value': '24'},
                                    {'label': '25', 'value': '25'},
                                    {'label': '26', 'value': '26'},
                                    {'label': '27', 'value': '27'},
                                    {'label': '28', 'value': '28'},
                                    {'label': '29', 'value': '29'},
                                    {'label': '30', 'value': '30'},
                                    {'label': '31', 'value': '31'},
                                    {'label': '32', 'value': '32'},
                                    {'label': '33', 'value': '33'},
                                    {'label': '34', 'value': '34'},
                                    {'label': '35', 'value': '35'},
                                    {'label': '36', 'value': '36'},
                                    {'label': '37', 'value': '37'},
                                    {'label': '38', 'value': '38'},
                                    {'label': '39', 'value': '39'},
                                    {'label': '40', 'value': '40'},
                                    {'label': '41', 'value': '41'},
                                    {'label': '42', 'value': '42'},
                                    {'label': '43', 'value': '43'},
                                    {'label': '44', 'value': '44'},
                                    {'label': '45', 'value': '45'},
                                    {'label': '46', 'value': '46'},
                                    {'label': '47', 'value': '47'},
                                    {'label': '48', 'value': '48'},
                                    {'label': '49', 'value': '49'},
                                    {'label': '50', 'value': '50'},
                                    {'label': '51', 'value': '51'},
                                    {'label': '52', 'value': '52'},
                                    {'label': '53', 'value': '53'},
                                    {'label': '54', 'value': '54'},
                                    {'label': '55', 'value': '55'},
                                    {'label': '56', 'value': '56'},
                                    {'label': '57', 'value': '57'},
                                    {'label': '58', 'value': '58'},
                                    {'label': '59', 'value': '59'},
                                    {'label': '60', 'value': '60'},
                                ]),
                            html.Label("Second", style={'font-family': 'Verdana', 'font-size': '12px'}),
                            dcc.Dropdown(
                                id='second', style={'font-family': 'Verdana', 'font-size': '12px'},
                                options=[
                                    {'label': '01', 'value': '01'},
                                    {'label': '02', 'value': '02'},
                                    {'label': '03', 'value': '03'},
                                    {'label': '04', 'value': '04'},
                                    {'label': '05', 'value': '05'},
                                    {'label': '06', 'value': '06'},
                                    {'label': '07', 'value': '07'},
                                    {'label': '08', 'value': '08'},
                                    {'label': '09', 'value': '09'},
                                    {'label': '10', 'value': '10'},
                                    {'label': '11', 'value': '11'},
                                    {'label': '12', 'value': '12'},
                                    {'label': '13', 'value': '13'},
                                    {'label': '14', 'value': '14'},
                                    {'label': '15', 'value': '15'},
                                    {'label': '16', 'value': '16'},
                                    {'label': '17', 'value': '17'},
                                    {'label': '18', 'value': '18'},
                                    {'label': '19', 'value': '19'},
                                    {'label': '20', 'value': '20'},
                                    {'label': '21', 'value': '21'},
                                    {'label': '22', 'value': '22'},
                                    {'label': '23', 'value': '23'},
                                    {'label': '24', 'value': '24'},
                                    {'label': '25', 'value': '25'},
                                    {'label': '26', 'value': '26'},
                                    {'label': '27', 'value': '27'},
                                    {'label': '28', 'value': '28'},
                                    {'label': '29', 'value': '29'},
                                    {'label': '30', 'value': '30'},
                                    {'label': '31', 'value': '31'},
                                    {'label': '32', 'value': '32'},
                                    {'label': '33', 'value': '33'},
                                    {'label': '34', 'value': '34'},
                                    {'label': '35', 'value': '35'},
                                    {'label': '36', 'value': '36'},
                                    {'label': '37', 'value': '37'},
                                    {'label': '38', 'value': '38'},
                                    {'label': '39', 'value': '39'},
                                    {'label': '40', 'value': '40'},
                                    {'label': '41', 'value': '41'},
                                    {'label': '42', 'value': '42'},
                                    {'label': '43', 'value': '43'},
                                    {'label': '44', 'value': '44'},
                                    {'label': '45', 'value': '45'},
                                    {'label': '46', 'value': '46'},
                                    {'label': '47', 'value': '47'},
                                    {'label': '48', 'value': '48'},
                                    {'label': '49', 'value': '49'},
                                    {'label': '50', 'value': '50'},
                                    {'label': '51', 'value': '51'},
                                    {'label': '52', 'value': '52'},
                                    {'label': '53', 'value': '53'},
                                    {'label': '54', 'value': '54'},
                                    {'label': '55', 'value': '55'},
                                    {'label': '56', 'value': '56'},
                                    {'label': '57', 'value': '57'},
                                    {'label': '58', 'value': '58'},
                                    {'label': '59', 'value': '59'},
                                    {'label': '60', 'value': '60'},
                                ]),
                        ]),
                    ]),
                    # Expire date
                    html.Tr(id="expires", style={'text-align': 'center', 'display': 'none'}, children=[
                        html.Label("Schedule expires on", style={'font-family': 'Verdana'}),
                        html.Br(),
                        dcc.DatePickerSingle(
                            id='schedule_expires',
                            initial_visible_month=date(today().year, today().month, today().day),
                            display_format='DD-MM-YYYY',
                            date=date(today().year, today().month, today().day),
                            style={'font-family': 'Verdana', 'font-size': '12px'}
                        ),
                        html.Br(),
                    ]),
                    # Never expires
                    html.Tr(id='never', style={'text-align': 'center', 'display': 'table-row'}, children=[
                        dcc.Checklist(id='never_check',
                                      options=[
                                          {'label': 'Schedule never expires', 'value': 'never'},
                                      ], value=['never'],
                                      ),
                        html.Br(),
                    ]),
                    # Add button
                    html.Tr(id='add', children=[
                        html.Button(id='add_trigger_button', children=[
                            html.Span([
                                html.Img(
                                    src='https://raw.githubusercontent.com/joostvangils/BPMN_RPA/main/BPMN_RPA/Images/add.png',
                                    style={'width': '25px'})
                            ])
                        ], style={'background-color': 'Transparent', 'border': 'none', 'cursor': 'pointer',
                                  'margin': '5px', 'float': 'right'}),
                        html.Div(id='empty_add', children=[], style={'display': 'none'}),
                    ]),
                ], style={'border': '1px solid #d9d9d9'}),
            ]),
        ], style={'vertical-align': 'top'}),
    ], style={'vertical-align': 'top'}),
    # Trigger table
    html.Tr(children=[
        html.Td(children=[
            html.H4("Installed flow triggers", style={'font-family': 'Verdana', 'margin': '4px'}),
        ]),
    ]),
    html.Tr(children=[
        # Registered datatable
        html.Td(children=[
            dash_table.DataTable(
                id='triggers',
                columns=triggers_columns,
                editable=False,
                data=triggers.to_dict('records'),
                sort_action='native',
                filter_action='native',
                style_table={'min-width': '300px'},
                style_cell={'textAlign': 'left', 'overflow': 'visible', 'textOverflow': 'ellipsis',
                            'height': '40px', 'font-family': 'Verdana', 'font-size': '12px'},
                style_header={'backgroundColor': 'rgb(0, 0, 153)', 'font-family': 'Verdana', 'fontWeight': 'bold',
                              'color': 'white', 'overflow': 'hidden', 'textOverflow': 'ellipsis'},
                style_data_conditional=[{'if': {'row_index': 'odd'}, 'backgroundColor': 'rgb(248, 248, 248)'},
                                        {'if': {'state': 'selected'}, 'backgroundColor': 'rgba(0, 116, 217, 0.3)',
                                         'border': '1px rgba(0, 116, 217, 0.3)'},
                                        ],
                # {'if': {'column_id': 'status', 'filter_query': '{result} eq "True"'}, 'width': '50%'}],
                # style_cell_conditional=[{'if': {'column_id': 'description'}, 'editable': True}],
                # style_header_conditional=[{'if': {'column_id': 'status'}, 'fontSize': '15px'}],
                page_action="native",
                page_current=0,
                page_size=10,

            )
        ], style={'vertical-align': 'top'}),
    ]),
    # Trigger delete button
    html.Tr(id='trigger_delete', children=[
        html.Td(children=[
            html.Button(id='delete_trigger_button', children=[
                html.Span([
                    html.Img(
                        src='https://raw.githubusercontent.com/joostvangils/BPMN_RPA/main/BPMN_RPA/Images/delete.png',
                        style={'width': '25px'})
                ])
            ], style={'background-color': 'Transparent', 'border': 'none', 'cursor': 'pointer', 'margin': '5px',
                      'float': 'right'}),
            html.Div(id='empty_add', style={'display': 'none'}),
        ], style={'border': '1px solid #d9d9d9'}),
    ]),
    dcc.ConfirmDialog(id='confirm', message='Are you sure you want to continue?'),

], style={'vertical-align': 'top'}),

# endregion

# region Callback functions Run page

# Global variables
selected_row = None


# region Add trigger to database
@app.callback(
    Output('empty_add', 'children'),
    [Input('add_trigger_button', 'n_clicks'), Input('selected_row', 'children'), Input('fire_trigger', 'value'),
     Input('specific_date', 'value'), Input('hour', 'value'),
     Input('minute', 'value'), Input('second', 'value'), Input('weekly_checklist', 'value'),
     Input('monthly_days', 'value'), Input('monthly_months', 'value'), Input('never_check', 'value'),
     Input('schedule_expires', 'value')]
)
def add_trigger(n_clicks, selectedrow, fire_trigger, specific_date, hour, minute, second, weekly_days, monthly_days,
                monthly_months, never_check, schedule_expires):
    if n_clicks is not None and selectedrow is not None:
        connection = sqlite3.connect(rf'{dbpath}\orchestrator.db')
        selected = json.loads(selected_row)
        item_id = selected.get('row_id')
        time = f"{hour}:{minute}:{second}"
        expires = False
        if never_check == "never":
            expires = True
        days = ",".join(weekly_days)
        days_of_month = ",".join(monthly_days)
        months = ",".join(monthly_months)
        sql = f"SELECT name FROM Registered WHERE id={item_id}"
        cur = connection.cursor()
        cur.execute(sql)
        name = cur.fetchone()[0]
        sql = f"INSERT INTO Triggers (registered_id, name, fire_trigger, time, expires, expires_on, date, days, days_of_month, months) VALUES ({item_id}, '{name}', '{fire_trigger}', '{time}', {expires}, '{schedule_expires}', '{specific_date}', '{days}', '{days_of_month}', '{months}') WHERE NOT EXISTS (SELECT id FROM Triggers WHERE registered_id = {item_id} AND fire_trigger='{fire_trigger}' AND time='{time}' AND expires={expires} AND expires_on='{schedule_expires}' AND date='{specific_date}' AND days='{days}' AND days_of_month='{days_of_month}' AND months='{months}' )"
        curs = connection.cursor()
        curs.execute(sql)
        connection.commit()
        return ""
    return ""


# endregion

# region Show selected trigger fields
@app.callback(
    [Output('daily', 'style'), Output('monthly', 'style'), Output('specific_dates', 'style'), Output('weekly', 'style'),
     Output('hour', 'value'), Output('minute', 'value'), Output('second', 'value')],
    Input('fire_trigger', 'value')
)
def trigger_select(value):
    now = datetime.now()
    if value is not None:
        if value == "daily":
            return {'display': 'table-row'}, {'text-align': 'center', 'display': 'none'}, {'text-align': 'center',
                                                                                           'display': 'none'}, {
                       'display': 'none'}, now.strftime("%H"), now.strftime("%M"), now.strftime("%S")
        if value == "specific_dates":
            return {'display': 'table-row'}, {'text-align': 'center', 'display': 'none'}, {'text-align': 'center',
                                                                                           'display': 'table-row'}, {
                       'display': 'none'}, now.strftime("%H"), now.strftime("%M"), now.strftime("%S")
        if value == "weekly":
            return {'display': 'table-row'}, {'text-align': 'center', 'display': 'none'}, {'text-align': 'center',
                                                                                           'display': 'none'}, {
                       'display': 'table-row'}, now.strftime("%H"), now.strftime("%M"), now.strftime("%S")
        if value == "monthly":
            return {'display': 'table-row'}, {'text-align': 'center', 'display': 'table-row'}, {'text-align': 'center',
                                                                                                'display': 'none'}, {
                       'display': 'none'}, now.strftime("%H"), now.strftime("%M"), now.strftime("%S")
    return {'display': 'table-row'}, {'text-align': 'center', 'display': 'none'}, {'text-align': 'center',
                                                                                   'display': 'none'}, {
               'display': 'none'}, now.strftime("%H"), now.strftime("%M"), now.strftime("%S")


# endregion

# region Show Schedule Expires
@app.callback(
    Output('expires', 'style'),
    Input('never_check', 'value')
)
def trigger_select(value):
    if value is not None:
        if len(value) == 0:
            return {'text-align': 'center', 'display': 'table-row'}
    return {'text-align': 'center', 'display': 'none'}


# endregion

# region Run a flow
@app.callback(
    Output('empty_run', 'children'),
    [Input('run_button', 'n_clicks'), Input('selected_row', 'children'), Input('registered', 'data')]
)
def run_a_flow(n_clicks, selected_row, data):
    ctx = dash.callback_context
    triggered = ctx.triggered[0]["prop_id"]
    if n_clicks is not None and str(triggered).lower().startswith("run_button"):
        connection = sqlite3.connect(rf'{dbpath}\orchestrator.db')
        selected = json.loads(selected_row)
        item_id = data[selected.get('row')]['id']
        cur = connection.cursor()
        cur.execute(f"SELECT * FROM Registered where id={item_id}")
        reg = cur.fetchone()
        flow = f"{dbpath}\\Registered Flows\\{reg[1]}.xml"
        # Start separate thread
        proc = multiprocessing.Process(target=flow_runner, args=(flow,))
        proc.start()
    return ""


# endregion

# region Edit a flow
@app.callback(
    Output('empty_edit', 'children'),
    [Input('edit_button', 'n_clicks'), Input('selected_row', 'children'), Input('registered', 'data')]
)
def edit_a_flow(n_clicks, selected_row, data):
    if n_clicks is not None:
        connection = sqlite3.connect(rf'{dbpath}\orchestrator.db')
        selected = json.loads(selected_row)
        item_id = data[selected.get('row')]['id']
        cur = connection.cursor()
        cur.execute(f"SELECT * FROM Registered where id={item_id}")
        reg = cur.fetchone()
        flow = f"{dbpath}\\Registered Flows\\{reg[1]}.xml"
        subprocess.Popen(f"{dbpath}\\drawio.exe -open {flow}")
    return ""


# endregion

# region Switch pages
@app.callback(dash.dependencies.Output('page-content', 'children'),
              [dash.dependencies.Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/run_page':
        return runpage_layout
    else:
        return mainpage_layout
    # You could also return a 404 "URL not found" page here


# endregion

# region Highlight selected row in Registered table
@app.callback(
    [Output('registered', 'style_data_conditional'), Output('selected_row', 'children')],
    Input('registered', 'active_cell')
)
def select_registered_row(active_cell):
    if active_cell is not None:
        style = [{'if': {'row_index': 'odd'}, 'backgroundColor': 'rgb(248, 248, 248)'},
                 {'if': {'row_index': active_cell["row"]}, 'backgroundColor': 'rgba(0, 116, 217, 0.3)'},
                 {'if': {'state': 'selected'}, 'backgroundColor': 'rgba(0, 116, 217, 0.3)',
                  'border': '1px rgba(0, 116, 217, 0.3)'}, ]
        active_cell = json.dumps(active_cell)
    else:
        style = [{'if': {'row_index': 'odd'}, 'backgroundColor': 'rgb(248, 248, 248)'},
                 {'if': {'state': 'selected'}, 'backgroundColor': 'rgba(0, 116, 217, 0.3)',
                  'border': '1px rgba(0, 116, 217, 0.3)'}, ]
        active_cell = ''
    return style, active_cell


# endregion

# region Update registered table data
# This callback is for Registering and deleting Flows
@app.callback([Output('registered', 'data'),
               Output('registered', 'columns')],
              [Input('datatable-upload', 'contents'), Input('selected_row', 'children'), Input('to_do', 'children'),
               Input('confirm', 'submit_n_clicks')],
              [State('datatable-upload', 'filename')],
              )
def update_output(contents, selected_row, to_do, submit_n_clicks, filename):
    connection = sqlite3.connect(rf'{dbpath}\orchestrator.db')
    if submit_n_clicks is not None and to_do == "delete_from_registered":
        selected = json.loads(selected_row)
        item_id = selected.get('row_id')
        sql = f"SELECT name FROM Registered WHERE id={item_id}"
        cur = connection.cursor()
        cur.execute(sql)
        name = cur.fetchone()[0]
        cur.execute(f"DELETE FROM Registered where id={item_id};")
        connection.commit()
        flow = f"{dbpath}\\Registered Flows\\{name}.xml"
        os.remove(flow)
    else:
        if contents is not None and str(filename).endswith(".xml"):
            name = filename.lower().split("\\")[-1].replace(".xml", "")
            path = rf"{dbpath}\Registered Flows\{name}.xml"
            xml = base64.b64decode(contents.split(",")[1])
            f = open(path, 'w', encoding="utf-8")
            f.write(xml.decode("utf-8"))
            f.close()
            sql = f"INSERT INTO Registered (name, location) SELECT '{name}','{filename}' WHERE NOT EXISTS (SELECT id FROM Registered WHERE name='{name}' and location='{filename}');"
            connection.cursor().execute(sql)
            connection.commit()
    sql = "Select id, name, description from Registered;"
    registered_flows = pd.read_sql_query(sql, connection)
    registered_flows_columns = [{"name": i, "id": i} for i in registered_flows.columns]
    decsription_column = [x for x in registered_flows_columns if x["id"] == "description"][0]
    decsription_column.update({'editable': True})
    return registered_flows.to_dict('records'), registered_flows_columns


# endregion

# region Ask question "are you sure?"
@app.callback([Output('confirm', 'displayed'), Output('confirm', 'message'), Output('to_do', 'children')],
              [Input('delete_button', 'n_clicks'), Input('selected_row', 'children')])
def ask_question_and_execute(n_clicks, selected_row):
    ctx = dash.callback_context
    triggered = ctx.triggered[0]["prop_id"]
    to_do = ""
    message = ""
    show_question = False
    if str(triggered).lower().startswith("delete_button"):
        connection = sqlite3.connect(rf'{dbpath}\orchestrator.db')
        selected = json.loads(selected_row)
        item_id = selected.get('row_id')
        sql = f"SELECT name FROM Registered WHERE id={item_id}"
        cur = connection.cursor()
        cur.execute(sql)
        name = cur.fetchone()[0]
        to_do = "delete_from_registered"
        message = f"Do you really want to delete flow '{name}'?"
        show_question = True
    return show_question, message, to_do


# endregion


# endregion


if __name__ == '__main__':
    app.run_server(debug=True)
