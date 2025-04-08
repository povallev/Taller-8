import dash
from dash import dcc  # dash core components
from dash import html # dash html components
from dash.dependencies import Input, Output
import psycopg2
from dotenv import load_dotenv # pip install python-dotenv
import os

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

env_path = "app2.env"

# load env 
load_dotenv(dotenv_path=env_path)
# extract env variables
USER = os.getenv('DBUSER')
PASSWORD = os.getenv('DBPASSWORD')
HOST = os.getenv('DBHOST')
PORT = os.getenv('DBPORT')
DBNAME = os.getenv('DBNAME')

# connect to DB
print(DBNAME)
print(USER)
print(PASSWORD)
print(HOST)
print(PORT)
engine = psycopg2.connect(
    dbname=DBNAME,
    user=USER,
    password=PASSWORD,
    host=HOST,
    port=PORT
)

# Cargar las opciones únicas para cada variable desde la base de datos
def get_unique_values(column):
    with engine.cursor() as cursor:
        cursor.execute(f"SELECT DISTINCT {column} FROM prodq1 ORDER BY {column}")
        return [row[0] for row in cursor.fetchall() if row[0] is not None]

# Lista de variables disponibles
variables = {
    "Trimestre": "quarter",
    "Departamento": "department",
    "Día": "day",
    "Equipo": "team"
}

app.layout = html.Div([
    html.H6("Seleccione una variable"),
    dcc.Dropdown(id='variable', value='quarter',
                 options=[{'label': k, 'value': v} for k, v in variables.items()]),
    html.Br(),
    html.H6("Seleccione un valor para la variable"),
    dcc.Dropdown(id='variable-value'),
    html.Br(),
    html.H6("Estadísticas:"),
    html.Div(["Productividad objetivo promedio:", html.Div(id='output-targeted')]),
    html.Div(["Productividad real promedio:", html.Div(id='output-actual')]),
])

@app.callback(
    Output('variable-value', 'options'),
    Input('variable', 'value')
)
def set_variable_value_options(selected_variable):
    try:
        unique_values = get_unique_values(selected_variable)
        return [{'label': val, 'value': val} for val in unique_values]
    except Exception as e:
        print(f"Error al obtener valores únicos: {e}")
        return []

@app.callback(
    Output('output-targeted', 'children'),
    Output('output-actual', 'children'),
    Input('variable', 'value'),
    Input('variable-value', 'value')
)
def update_output_div(variable, variable_value):
    try:
        with engine.cursor() as cursor:
            query_productivity = f"""
            SELECT avg(targeted_productivity) as avg_targeted, avg(actual_productivity) as avg_actual
            FROM prodq1
            WHERE {variable} = %s;"""
            cursor.execute(query_productivity, (variable_value,))
            result = cursor.fetchone()

            avg_targeted = result[0] if result and result[0] is not None else 0
            avg_actual = result[1] if result and result[1] is not None else 0

            return '{:.2f}'.format(avg_targeted), '{:.2f}'.format(avg_actual)

    except Exception as e:
        print(f"Error al ejecutar la consulta: {e}")
        return "Error en la consulta", "Error en la consulta"

if __name__ == '__main__':
    app.run(debug=True, port=8040)
