import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
from pymongo import MongoClient
from bson import ObjectId
import pandas as pd
import plotly.express as px
import requests

# Fonction pour se connecter à MongoDB
def connexionMongo():
    client = MongoClient("mongodb://localhost:27017/")
    return client

# Fonction pour insérer des données dans MongoDB
def insertMongo(nameC, datas):
    client = connexionMongo()
    collection = client["airlabs"][nameC]
    collection.insert_many(datas)

# Fonction pour obtenir des données depuis MongoDB
def getDatasMongo(nameC, query):
    client = connexionMongo()
    collection = client["airlabs"][nameC]
    resultats = collection.find(query)
    return resultats

# Définir les couleurs des jours
custom_colors = {
    "mon": "#ff9900",
    "tue": "#cccc00",
    "wed": "#ff0066",
    "thu": "#0066ff",
    "fri": "#00ff00",
    "sat": "#cc00cc",
    "sun": "#993300"
}

# Récupérer les données des pays
query_countries = {}
dfCountries = pd.DataFrame(list(getDatasMongo("countries", query_countries)))
query_airport = {"iata_code": {"$exists": True, "$ne": None}}
dfAirports = pd.DataFrame(list(getDatasMongo("airports", query_airport)))

# Initialiser l'application Dash
app = dash.Dash(__name__, suppress_callback_exceptions=True)

# Layout de la page index
index_page = html.Div([
    html.H1("Projet Airlines Dashboard"),
    dcc.Link(html.Button('Liste de l\'aéroport'), href='/airports'),
    html.Br(),
    html.Br(),
    dcc.Link(html.Button('Liste des horaires'), href='/volsfromto'),
    html.Br(),
    html.Br(),
    dcc.Link(html.Button('Statistiques des vols par Jour de la Semaine'), href='/voldays'),
    html.Br(),
    html.Br(),
    dcc.Link(html.Button('Information du vol en passant par FastAPI'), href='/flight_info')])

# Layout de la page airports
airports_layout = html.Div([
    html.H1("Liste de l'aéroport"),
    dcc.Link(html.Button('Revenir à la page d\'accueil'), href='/index_page'),
    html.Br(),
    html.Br(),
    html.Label("Sélectionnez le pays :"),
    dcc.Dropdown(
        id='country-dropdown',
        options=[
            {'label': country, 'value': country}
            for country in dfCountries['code'].unique()
        ],
        multi=True
    ),
    html.Div(id='airport-stats')
])
# Ajouter le layout de la page airports à l'application
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

# Callback pour mettre à jour les statistiques de l'aéroport en fonction du pays sélectionné
@app.callback(
    Output('airport-stats', 'children'),
    [Input('country-dropdown', 'value')]
)
def update_airport_stats(selected_countries):
    if selected_countries:
        stats_tables = []

        for country_code in selected_countries:
            query = {"country_code": country_code}
            resultats = getDatasMongo("airports", query)

            datas = []
            for item in resultats:
                # Convertir ObjectId en str si présent
                item_dict = {key: str(value) if key == "_id" and isinstance(value, ObjectId) else value for key, value in
                             item.items()}
                datas.append(item_dict)

            selected_data = pd.DataFrame(datas)
            stats_table = html.Table(
                # En-tête du tableau
                [html.Tr([html.Th(col) for col in selected_data.columns])] +
                # Lignes de données
                [html.Tr([html.Td(selected_data.iloc[i][col]) for col in selected_data.columns]) for i in
                 range(len(selected_data))]
            )

            stats_tables.append(stats_table)

        return stats_tables
    else:
        return html.Div("Sélectionnez au moins un pays pour afficher les statistiques de l'aéroport.")

# Layout de la page volsdays
voldays_layout = html.Div([
    html.H1("Statistiques des Vols par Jour de la Semaine"),
    dcc.Link(html.Button('Revenir à la page d\'accueil'), href='/index_page'),
    html.Br(),
    dcc.Graph(id='volsdays-graph')
])

# Ajouter le layout de la page volsdays à l'application
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])
# Callback pour mettre à jour le graphique des vols par jour de la semaine
@app.callback(
    Output('volsdays-graph', 'figure'),
    [Input('url', 'pathname')]
)
def update_voldays_graph(pathname):
    if pathname == '/voldays':
        # Récupérer les données de la collection "routes"
        query = {}
        resultats = getDatasMongo("routes", query)

        # Créer un DataFrame à partir des résultats
        df_routes = pd.DataFrame(list(resultats))

        # Compter le nombre de vols par jour de la semaine
        df_volsdays = df_routes['days'].explode().value_counts().sort_index()

        # Créer un graphique à barres avec des couleurs personnalisées
        fig = px.bar(
            x=df_volsdays.index,
            y=df_volsdays.values,
            labels={'x': 'Jour de la semaine', 'y': 'Nombre de vols'},
            title='Statistiques des Vols par Jour de la Semaine',
            color=df_volsdays.index.map(custom_colors)
        )

        return fig
    else:
        return dash.no_update

# Layout de la page volsfromto
volsfromto_layout = html.Div([
    html.H1("Liste des horaires depuis l'aéroport de départ vers l'aéroport d'arrivée"),
    dcc.Link(html.Button('Revenir à la page d\'accueil'), href='/index_page'),
    html.Br(),
    html.Br(),
    html.Label("Sélectionnez l'aéroport de départ :"),
    dcc.Dropdown(
        id='dep-iata-dropdown',
        options=[
            {'label': dep_iata, 'value': dep_iata}
            for dep_iata in dfAirports['iata_code'].unique()
        ],
        multi=False
    ),
    html.Label("Sélectionnez l'aéroport d'arrivée :"),
    dcc.Dropdown(
        id='arr-iata-dropdown',
        options=[
            {'label': arr_iata, 'value': arr_iata}
            for arr_iata in dfAirports['iata_code'].unique()
        ],
        multi=False
    ),
    html.Div(id='schedules-list')
])

# Callback pour mettre à jour la liste des horaires en fonction des aéroports sélectionnés
@app.callback(
    Output('schedules-list', 'children'),
    [Input('dep-iata-dropdown', 'value'),
     Input('arr-iata-dropdown', 'value')]
)
def update_schedules_list(dep_iata, arr_iata):
    if dep_iata and arr_iata:
        stats_tables = []
        # Construire la requête pour obtenir les horaires
        query = {"dep_iata": dep_iata, "arr_iata": arr_iata}
        resultats = getDatasMongo("schedules", query)

        datas = []
        for item in resultats:
            # Convertir ObjectId en str si présent
            item_dict = {key: str(value) if key == "_id" and isinstance(value, ObjectId) else value for key, value in
                         item.items()}
            datas.append(item_dict)

        selected_data = pd.DataFrame(datas)
        stats_table = html.Table(
            # En-tête du tableau
            [html.Tr([html.Th(col) for col in selected_data.columns])] +
            # Lignes de données
            [html.Tr([html.Td(selected_data.iloc[i][col]) for col in selected_data.columns]) for i in
             range(len(selected_data))]
        )

        stats_tables.append(stats_table)
        return stats_tables
    else:
        return html.Div("Sélectionnez l'aéroport de départ et l'aéroport d'arrivée pour afficher les horaires.")

# Layout for the flight_info page
flight_info_layout = html.Div([
    html.H1("Information du vols via FastAPI"),
    dcc.Link(html.Button('Revenir à la page d\'accueil'), href='/index_page'),
    html.Br(),
    html.Br(),
    html.Label("Sélectionnez le code IATA du vol :"),
    dcc.Input(id='flight-iata-input', type='text', value=''),
    html.Button('Obtenir Information', id='flight-info-button'),
    html.Div(id='flight-info-output')
])

# Add the layout for the flight_info page to the application
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

# Callback to update flight info based on the flight_iata parameter
@app.callback(
    Output('flight-info-output', 'children'),
    [Input('flight-info-button', 'n_clicks')],
    [State('flight-iata-input', 'value')]
)
def update_flight_info(n_clicks, flight_iata):
    if n_clicks is not None and flight_iata:
        # Make a request to the FastAPI endpoint
        fastapi_url = f'http://localhost:8000/flight_info?flight_iata={flight_iata}'
        response = requests.get(fastapi_url)

        if response.status_code == 200:
            flight_info = response.json()
            # Display the flight information
            return html.Div([
                html.Br(),
                html.Br(),
                html.Label(f"Information du vols : {flight_iata}:"),
                html.P(f"Aéroport départ: {flight_info[0]['dep_iata']}"),
                html.P(f"Terminal départ: {flight_info[0]['dep_terminal']}"),
                html.P(f"Porte départ: {flight_info[0]['dep_gate']}"),
                html.P(f"Heure de départ: {flight_info[0]['dep_time']}"),
                html.P(f"Heure de départ estimé: {flight_info[0]['dep_estimated']}"),
                html.P(f"Heure de départ réel: {flight_info[0]['dep_actual']}"),
                html.P(f"Aéroport arrivée: {flight_info[0]['arr_iata']}"),
                html.P(f"Terminal arrivée: {flight_info[0]['arr_terminal']}"),
                html.P(f"Porte arrivée: {flight_info[0]['arr_gate']}"),
            ])
        else:
            return html.Div(f"Error: Information introuvable {flight_iata}")
    else:
        return html.Div("Entrer flight IATA code et puis cliquer 'Obtenir Information'.")

# Callback pour afficher la page appropriée en fonction de l'URL
@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/airports':
        return airports_layout
    elif pathname == '/voldays':
        return voldays_layout
    elif pathname == '/volsfromto':
        return volsfromto_layout
    elif pathname == '/flight_info':
        return flight_info_layout
    else:
        return index_page


# Exécuter l'application Dash
if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0',port=7777)