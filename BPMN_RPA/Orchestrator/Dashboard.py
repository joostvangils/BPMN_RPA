import base64
import copy
import os
import sqlite3
import winreg
from io import BytesIO
from typing import Any

import PIL
import dash_table
import pandas as pd
import dash
from PIL.Image import Image
from dash.dependencies import Input, Output, State
import dash_html_components as html
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
import dash_core_components as dcc

# region Functions and globals
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

sql = "Select id, name, description from Registered"
registered_flows = pd.read_sql_query(sql, connection)
registered_flows_columns = [{"name": i, "id": i} for i in registered_flows.columns]
decsription_column = [x for x in registered_flows_columns if x["id"] == "description"][0]
decsription_column.update({'editable': True})

sql = f"SELECT id, name, result, started, finished FROM Workflows;"
flows = pd.read_sql_query(sql, connection)
flows = add_images_to_dataframe(flows, "result")
flows_columns = get_columns_with_image_from_dataframe(flows, "result")


sql = f"SELECT id, workflow, name, status, step, result, timestamp as executed FROM Steps;"
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
        style_cell={'textAlign': 'left', 'overflow': 'visible', 'textOverflow': 'ellipsis', 'height': '40px', 'font-family': 'Verdana', 'font-size': '12px',
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
        style_cell={'textAlign': 'left', 'overflow': 'visible', 'textOverflow': 'ellipsis', 'height': '40px', 'font-family': 'Verdana', 'font-size': '12px'},
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
    # endregion
])
# endregion

# region CallBack functions main page
@app.callback(
    [Output('flows', 'style_data_conditional'), Output('steps', 'data')],
    Input('flows', 'active_cell')
)
def select_row_filter_data(active_cell):
    connection = sqlite3.connect(rf'{dbpath}\orchestrator.db')
    if active_cell is not None:
        style = [{'if': {'row_index': 'odd'}, 'backgroundColor': 'rgb(248, 248, 248)'},
                 {'if': {'row_index': active_cell["row"]}, 'backgroundColor': 'rgba(0, 116, 217, 0.3)'},
                 {'if': {'state': 'selected'}, 'backgroundColor': 'rgba(0, 116, 217, 0.3)',
                  'border': '1px rgba(0, 116, 217, 0.3)'}, ]
        sql = f"SELECT id, workflow, name, status, step, result, timestamp as executed FROM Steps WHERE workflow = {active_cell['row_id']} ;"
        steps = pd.read_sql_query(sql, connection)
        steps = add_images_to_dataframe(steps)
    else:
        style = [{'if': {'row_index': 'odd'}, 'backgroundColor': 'rgb(248, 248, 248)'},
                 {'if': {'state': 'selected'}, 'backgroundColor': 'rgba(0, 116, 217, 0.3)',
                  'border': '1px rgba(0, 116, 217, 0.3)'}, ]
        sql = f"SELECT id, workflow, name, status, step, result, timestamp as executed FROM Steps;"
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
            html.Td(children=[
                dash_table.DataTable(
                        id='registered',
                        columns=registered_flows_columns,
                        editable=False,
                        data=registered_flows.to_dict('records'),
                        sort_action='native',
                        filter_action='native',
                        style_table={'min-width': '300px'},
                        style_cell={'textAlign': 'left', 'overflow': 'visible', 'textOverflow': 'ellipsis', 'height': '40px', 'font-family': 'Verdana', 'font-size': '12px'},
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
            ]),  # style={'border-collapse': 'collapse', 'border-spacing': 0, 'border-top': '2em solid transparent'}),
            html.Td([
                html.Table(children=[
                    html.Tr(children=[
                       html.Th(children=["Register Flows"], style={'backgroundColor': 'rgb(0, 0, 153)', 'font-family': 'Verdana', 'font-size': '15px', 'height': '38px', 'width': '300px', 'fontWeight': 'bold',
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
                                    'borderWidth': '1px', 'borderStyle': 'dashed', 'font-size': '12px', 'font-family': 'Verdana',
                                    'borderRadius': '5px', 'textAlign': 'center'},
                            ),
                            dash_table.DataTable(id='datatable-upload-container'),
                            ])
                        ]),
                    ]),
                ], style={'margin-top': '-1px'}),
                html.Table(children=[
                    html.Tr(children=[
                        html.Th(children=["Run Flows"],
                                style={'backgroundColor': 'rgb(0, 0, 153)', 'font-family': 'Verdana',
                                       'font-size': '15px', 'height': '38px', 'width': '300px', 'fontWeight': 'bold',
                                       'color': 'white', 'overflow': 'hidden', 'textOverflow': 'ellipsis'})
                    ])
                ])
            ], style={'vertical-align': 'top'}),
        ]),
    ]),
])
# endregion

# Callback functions Run page
@app.callback(dash.dependencies.Output('page-content', 'children'),
              [dash.dependencies.Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/run_page':
        return runpage_layout
    else:
        return mainpage_layout
    # You could also return a 404 "URL not found" page here


@app.callback(
    Output('registered', 'style_data_conditional'),
    Input('registered', 'active_cell')
)
def select_registered_row_filter_data(active_cell):
    if active_cell is not None:
        style = [{'if': {'row_index': 'odd'}, 'backgroundColor': 'rgb(248, 248, 248)'},
                 {'if': {'row_index': active_cell["row"]}, 'backgroundColor': 'rgba(0, 116, 217, 0.3)'},
                 {'if': {'state': 'selected'}, 'backgroundColor': 'rgba(0, 116, 217, 0.3)',
                  'border': '1px rgba(0, 116, 217, 0.3)'}, ]
    else:
        style = [{'if': {'row_index': 'odd'}, 'backgroundColor': 'rgb(248, 248, 248)'},
                 {'if': {'state': 'selected'}, 'backgroundColor': 'rgba(0, 116, 217, 0.3)',
                  'border': '1px rgba(0, 116, 217, 0.3)'}, ]
    return style


@app.callback([Output('registered', 'data'),
               Output('registered', 'columns')],
              [Input('datatable-upload', 'contents')],
              [State('datatable-upload', 'filename')])
def update_output(contents, filename):
    connection = sqlite3.connect(rf'{dbpath}\orchestrator.db')

    if contents is not None and str(filename).endswith(".xml"):
        name = filename.lower().split("\\")[-1].replace(".xml", "")
        sql = f"INSERT INTO Registered (name, location) SELECT '{name}','{filename}' WHERE NOT EXISTS (SELECT id FROM Registered WHERE name='{name}' and location='{filename}');"
        connection.cursor().execute(sql)
        connection.commit()
    sql = "Select id, name, description from Registered;"
    registered_flows = pd.read_sql_query(sql, connection)
    registered_flows_columns = [{"name": i, "id": i} for i in registered_flows.columns]
    decsription_column = [x for x in registered_flows_columns if x["id"] == "description"][0]
    decsription_column.update({'editable': True})
    return registered_flows.to_dict('records'), registered_flows_columns
    # df = parse_contents(contents, filename)
    # return df.to_dict('records'), [{"name": i, "id": i} for i in df.columns]

# endregion



if __name__ == '__main__':
    app.run_server(debug=True)
