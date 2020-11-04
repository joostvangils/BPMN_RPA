import base64
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
from dash.dependencies import Input, Output
import dash_html_components as html
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
import dash_core_components as dcc


# region Functions
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


# endregion

app = dash.Dash(__name__)
server = app.server
dbpath = get_reg('dbPath')
connection = sqlite3.connect(rf'{dbpath}\orchestrator.db')

sql = f"SELECT id, name, result, started, finished FROM Workflows;"
flows = pd.read_sql_query(sql, connection)
flows = add_images_to_dataframe(flows, "result")
flows_columns = get_columns_with_image_from_dataframe(flows, "result")

sql = f"SELECT id, workflow, name, status, step, result, timestamp as executed FROM Steps;"
steps = pd.read_sql_query(sql, connection)
steps = add_images_to_dataframe(steps)
step_columns = get_columns_with_image_from_dataframe(steps)
workflow_column = [x for x in step_columns if x["id"]=="workflow"][0]
workflow_column.update({'hideable': True})
app = dash.Dash(name="BPMN RPA", title="BPMN RPA")
app.layout = html.Div([

    html.Span([
        html.Img(src="https://raw.githubusercontent.com/joostvangils/BPMN_RPA/main/BPMN_RPA/Images/BPMN_RPA_logo.PNG",
                 width="280px", height="55px", style={'float': 'left'}),
        html.Br(),
        html.H2("Orchestrator", style={'font-family': 'Verdana', 'text-indent': '15px', 'margin': '4px'}),
        html.H4("Executed flows", style={'font-family': 'Verdana', 'margin': '4px'}),
    ], style={'white-space': 'nowrap'}),

    dash_table.DataTable(
        id='flows',
        columns=flows_columns,
        editable=False,
        data=flows.to_dict('records'),
        sort_action='native',
        filter_action='native',
        style_cell={'textAlign': 'left', 'overflow': 'visible', 'textOverflow': 'ellipsis', 'height': '40px',
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
        style_cell={'textAlign': 'left', 'overflow': 'visible', 'textOverflow': 'ellipsis', 'height': '40px'},
        style_header={'backgroundColor': 'rgb(0, 0, 153)', 'font-family': 'Verdana', 'fontWeight': 'bold',
                      'color': 'white', 'overflow': 'hidden', 'textOverflow': 'ellipsis'},
        style_data_conditional=[{'if': {'row_index': 'odd'}, 'backgroundColor': 'rgb(248, 248, 248)'}],
        # {'if': {'column_id': 'status', 'filter_query': '{result} eq "True"'}, 'width': '50%'}],
        style_cell_conditional=[{'if': {'column_id': 'started'}}],
        # style_header_conditional=[{'if': {'column_id': 'status'}, 'fontSize': '15px'}],
        page_action="native",
        page_current=0,
        page_size=10,

    ),
    # html.Button('Start', id='button'),
    html.Div(id='output-container'),
    # dcc.Interval(id="progress-interval", n_intervals=0, interval=500),
    # dbc.Progress(id="progress", color="info"),
])


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


# @app.callback(
#     [Output("progress", "value"), Output("progress", "children")],
#     [Input("progress-interval", "n_intervals")],
# )
# def update_progress(n):
#     # check progress of some background process, in this example we'll just
#     # use n_intervals constrained to be in 0-100
#     progress = min(n % 110, 100)
#     # only add text after 5% progress to ensure text isn't squashed too much
#     return progress, f"{progress} %" if progress >= 5 else ""


# @app.callback(
#     dash.dependencies.Output('output-container-button', 'children'),
#     [dash.dependencies.Input('button', 'n_clicks')])
# def run_script_onClick(n_clicks):
#     # Don't run unless the button has been pressed...
#     if not n_clicks:
#         raise PreventUpdate
#     script_fn = r'C:\temp\test.py'
#     return os.system(rf"python {script_fn}")


if __name__ == '__main__':
    app.run_server(debug=True)
