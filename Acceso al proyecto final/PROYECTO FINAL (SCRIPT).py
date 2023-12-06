from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium import webdriver
import pandas as pd
import time
import mysql.connector
import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
import plotly.express as px
from dash.dependencies import Input, Output

a = Service(ChromeDriverManager().install())
opc = Options()
opc.add_argument("--window-size=700,620")

data = []

years = [str(year) for year in range(2011, 2023)]

navegador = webdriver.Chrome(service=a, options=opc)
navegador.get("https://www.inegi.org.mx/temas/incidencia/")

time.sleep(5)

time.sleep(5)

entidades = navegador.find_elements(By.CLASS_NAME, "TdInicio")

for entidad in entidades:
    entidad_text = entidad.text.strip()

    if entidad_text.endswith("/1") or entidad_text.endswith("/2") or entidad_text.endswith("/3"):
        continue

    entidad_data = {"Entidad": entidad_text}
    entidad_datos = entidad.find_elements(By.XPATH, "following-sibling::td[@class='Td']")
    for i, tasa_element in enumerate(entidad_datos):
        if i < len(years):
            tasa_incidente_text = tasa_element.text.strip().replace(",", "")
            entidad_data[years[i]] = tasa_incidente_text

    data.append(entidad_data)

navegador.quit()

df = pd.DataFrame(data)
df = df.iloc[:-5]

entidades_a_eliminar = ["Estados Unidos Mexicanos"]
df = df[~df['Entidad'].isin(entidades_a_eliminar)]

#Conexion con tabla en MySQL e insercion de datos
conexion = mysql.connector.connect(
    host='127.0.0.1',
    port=3306,
    user='root',
    password='',
    db='CrimenesMex1'
)

# Crear un cursor
cursor = conexion.cursor()

# Insertar datos en la tabla Estados
insertar_estado = "INSERT INTO Estados (Estado) VALUES (%s)"

# Obtener los datos únicos de la columna 'Entidad' del DataFrame
entidades_unicas = df['Entidad'].unique()

# Limpiar los nombres de entidades en df y en el diccionario idestados
df['Entidad'] = df['Entidad'].str.strip()

# Iterar sobre las entidades y realizar las inserciones en la tabla Estados
for entidad in entidades_unicas:
    cursor.execute(insertar_estado, (entidad.strip(),))

# Confirmar las transacciones
conexion.commit()

# Cerrar el cursor y la conexión
cursor.close()
conexion.close()

# DataFrame en un archivo CSV
df.to_csv("datasets/incidencia_delictiva_mexico.csv", index=False)
df = pd.read_csv("datasets/incidencia_delictiva_mexico.csv")

print(df)

df_long = pd.melt(df, id_vars=['Entidad'], var_name='Año', value_name='Valor')

df_long['Año'] = df_long['Año'].astype(int)

# Figura con el DataFrame transformado
fig_bubble = px.scatter(df_long, x="Año", y="Valor", size="Valor", color="Entidad",
                        hover_name="Entidad", size_max=60)

# Inicialización de la aplicación Dash
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Dropdowns para la selección de año y estado
dropdown_year = dcc.Dropdown(
    id='year_dropdown',
    options=[{'label': 'Total', 'value': 'Total'}] +
            [{'label': str(year), 'value': year} for year in sorted(df_long['Año'].unique())],
    value='Total',
    clearable=False
)

dropdown_estado = dcc.Dropdown(
    id='estado_dropdown',
    options=[{'label': 'Total', 'value': 'Total'}] +
            [{'label': estado, 'value': estado} for estado in df_long['Entidad'].unique()],
    value='Total',
    clearable=False
)

# Layout de la aplicación
app.layout = html.Div([
    dbc.Container([
        dbc.Row([
            dbc.Col(html.H1("Incidencia Delictiva"), width={'size': 6, 'offset': 3}),
        ]),
        dbc.Row([
            dbc.Col(dropdown_year, width=6),
            dbc.Col(dropdown_estado, width=6)
        ]),
        dbc.Row([
            dbc.Col(dcc.Graph(id='bubble_chart'), width=6),
            dbc.Col(dcc.Graph(id='pie_chart'), width=6),
        ]),
        dbc.Row([
            dbc.Col(dbc.Card(id='estado_info', body=True), width=6),
            dbc.Col(dbc.Card(id='promedio_info', body=True), width=6)
        ]),
        dbc.Row([
            dbc.Col(dcc.Graph(id='bar_chart'), width=12),
        ]),
        dbc.Row([
            dbc.Col(dcc.Graph(id='bar_chart_zona'), width=12),
        ]),
    ]),
])


# Función para calcular el cambio porcentual
def calculate_percentage_change(current_value, previous_value):
    if previous_value == 0:
        return 0
    return ((current_value - previous_value) / previous_value) * 100


# Callback para la actualización de gráficos e información
@app.callback(
    [Output('bubble_chart', 'figure'),
     Output('pie_chart', 'figure'),
     Output('estado_info', 'children'),
     Output('promedio_info', 'children'),
     Output('bar_chart', 'figure'),
     Output('bar_chart_zona', 'figure')],
    [Input('year_dropdown', 'value'),
     Input('estado_dropdown', 'value')]
)
def update_charts_and_info(selected_year, selected_estado):
    # Filtro de datos
    if selected_year != 'Total':
        year_df = df_long[df_long['Año'] == selected_year]
    else:
        year_df = df_long

    if selected_estado != 'Total':
        estado_df = year_df[year_df['Entidad'] == selected_estado]
    else:
        estado_df = year_df

    # Gráficas de Plotly
    fig_bubble = px.scatter(estado_df, x="Año", y="Valor", size="Valor", color="Entidad", hover_name="Entidad",
                            size_max=60)
    fig_pie = px.pie(estado_df, values='Valor', names='Entidad')

    # Información del estado
    estado_info_content = [
        html.H4(f"Incidencia en {selected_estado}" if selected_estado != 'Total' else "Incidencia Total",
                className="card-title"),
        html.P(f"Delitos: {estado_df['Valor'].sum()}", className="card-text"),
    ]

    # Información del promedio
    promedio = year_df['Valor'].mean()
    promedio_info_content = [
        html.H4("Promedio Nacional" if selected_year != 'Total' else "Promedio General", className="card-title"),
        html.P(f"Promedio de delitos: {promedio:.2f}", className="card-text"),
    ]

    # Gráfica de barras general
    fig_bar = px.bar(year_df, x='Entidad', y='Valor', title='Incidencia Delictiva por Estado')

    # Clasificación por zonas y gráfica de barras por zona
    zonas = {
        "Noroeste": ["Baja California", "Baja California Sur", "Sinaloa", "Sonora"],
        "Noreste": ["Coahuila de Zaragoza", "Nuevo León", "Tamaulipas", "Chihuahua", "Durango", "Zacatecas", "San Luis Potosí"],
        "Occidente": ["Aguascalientes", "Colima", "Guanajuato", "Jalisco", "Michoacán de Ocampo", "Nayarit", "Querétaro"],
        "Centro": ["Ciudad de México",  "México", "Hidalgo", "Morelos", "Puebla", "Tlaxcala"],
        "Sur": ["Guerrero", "Oaxaca", "Chiapas", "Veracruz de Ignacio de la Llave"],
        "Sureste":["Campeche","Quintana Roo","Tabasco", "Yucatán"]}

    df_long['Zona'] = df_long['Entidad'].apply(
        lambda x: next((zona for zona, estados in zonas.items() if x in estados), 'Otra'))
    if selected_estado != 'Total':
        zona_seleccionada = df_long[df_long['Entidad'] == selected_estado]['Zona'].iloc[0]
        df_zona = df_long[df_long['Zona'] == zona_seleccionada]
        fig_bar_zona = px.bar(df_zona, x='Entidad', y='Valor', title=f'Comparación en Zona {zona_seleccionada}')
    else:
        fig_bar_zona = px.bar(df_long, x='Entidad', y='Valor', title='Incidencia Delictiva por Estado')

    return fig_bubble, fig_pie, estado_info_content, promedio_info_content, fig_bar, fig_bar_zona


# Ejecución del servidor Dash
if __name__ == '__main__':
    app.run_server(debug=True)