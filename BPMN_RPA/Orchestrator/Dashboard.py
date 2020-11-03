import base64
import os
import sqlite3
import winreg
from io import BytesIO

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


def get_reg(name):
    try:
        REG_PATH = r"SOFTWARE\BPMN_RPA"
        registry_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_PATH, 0, winreg.KEY_READ)
        value, regtype = winreg.QueryValueEx(registry_key, name)
        winreg.CloseKey(registry_key)
        return value
    except WindowsError:
        return None


app = dash.Dash(__name__)
server = app.server
dbpath = get_reg('dbPath')
connection = sqlite3.connect(rf'{dbpath}\orchestrator.db')
sql = f"SELECT * FROM Workflows;"
df = pd.read_sql_query(sql, connection)
t = 0
for row in df.iterrows():
    df.at[t, "parent"] = "![image description](https://www.iconsdb.com/icons/preview/green/ok-xxl.png){height=40px width=50px}"
    t += 1
columns = [{"name": i, "id": i} for i in df.columns]
imagecolumn = [element for element in columns if element['name'] == "parent"][0]
imagecolumn["presentation"] = "markdown"
imagecolumn["editable"] = False
app = dash.Dash(name="BPMN RPA", title="BPMN RPA")

app.layout = html.Div([

    html.H1("BPMN RPA Orchestrator", style={'font-family': 'Verdana'}),

    dash_table.DataTable(
        id='table',
        columns=columns,
        data=df.to_dict('records'),
        sort_action='native',
        filter_action='native',
        style_header={'backgroundColor': 'rgb(0, 0, 153)', 'font-family': 'Verdana', 'fontWeight': 'bold',
                      'color': 'white', 'overflow': 'hidden', 'textOverflow': 'ellipsis', 'maxHeight': 0},
        style_data_conditional=[{'if': {'row_index': 'odd'}, 'backgroundColor': 'rgb(248, 248, 248)'}],
        page_action="native",
        page_current= 0,
        page_size= 10,
    ),
    html.Button('Start', id='button'),
    html.Div(id='output-container-button'),
    dcc.Interval(id="progress-interval", n_intervals=0, interval=500),
    dbc.Progress(id="progress", color="info"),
])


@app.callback(
    [Output("progress", "value"), Output("progress", "children")],
    [Input("progress-interval", "n_intervals")],
)
def update_progress(n):
    # check progress of some background process, in this example we'll just
    # use n_intervals constrained to be in 0-100
    progress = min(n % 110, 100)
    # only add text after 5% progress to ensure text isn't squashed too much
    return progress, f"{progress} %" if progress >= 5 else ""


@app.callback(
    dash.dependencies.Output('output-container-button', 'children'),
    [dash.dependencies.Input('button', 'n_clicks')])
def run_script_onClick(n_clicks):
    # Don't run unless the button has been pressed...
    if not n_clicks:
        raise PreventUpdate
    script_fn = r'C:\temp\test.py'
    return os.system(rf"python {script_fn}")


if __name__ == '__main__':
    app.run_server(debug=True)
