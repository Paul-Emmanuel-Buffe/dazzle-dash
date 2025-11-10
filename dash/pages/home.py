import dash
from dash import html
import dash_bootstrap_components as dbc

dash.register_page(__name__, path="/", name="Accueil")

layout = html.Div([
    html.H1("Bienvenue dans le Dashboard Global du Groupe"),
    html.P("""Ce portail centralise les analyses des différents membres du groupe :
    Santé, Production alimentaire, Trafic aerien."""),
    html.Hr(),
    dbc.Row([
        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.H4(" Santé & IDH"),
                html.P("Analyse des tendances sanitaires mondiales."),
                dbc.Button("Accéder", href="/sante_idh", color="primary")
            ])
        ], class_name="mb-3")),
        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.H4(" Alimentation Mondiale"),
                html.P("Analyse de la production alimentaire par pays."),
                dbc.Button("Accéder", href="/economie", color="info")
            ])
        ], class_name="mb-3")),
        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.H4(" Trafic Aerien"),
                html.P("Analyse du trafic aérien."),
                dbc.Button("Accéder", href="/demographie", color="success")
            ])
        ], class_name="mb-3")),
    ])
])
