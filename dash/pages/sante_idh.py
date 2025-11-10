import dash
from dash import html, dcc, Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
import numpy as np
import plotly.graph_objects as go

dash.register_page(__name__, path="/sante_idh", name="Santé & IDH")

# ================================
# 🔹 Load data
# ================================
faits = pd.read_csv("data/Faits_Sante.csv")
dim_pays = pd.read_csv("data/Dim_Pays.csv")
dim_annee = pd.read_csv("data/Dim_Annee.csv")
dim_socio = pd.read_csv("data/Dim_SocioEconomique.csv")
dim_sante = pd.read_csv("data/Dim_Sante.csv")

# Fusion
df = (
    faits
    .merge(dim_pays, on="id_pays", how="left")
    .merge(dim_annee, on="id_annee", how="left")
    .merge(dim_socio, on="id_socio", how="left")
    .merge(dim_sante, on="id_sante", how="left") 
)

# Gestion valeurs manquantes IDH si absent
if "IDH" not in df.columns:
    # Si l’utilisateur n’a pas généré la colonne IDH, on la calcule
    if {"indice_revenu", "annees_scolarisation", "esperance_vie"}.issubset(df.columns):
        df["IDH"] = (
            df["indice_revenu"].clip(0, 1) +
            (df["annees_scolarisation"] / df["annees_scolarisation"].max()) +
            (df["esperance_vie"] / df["esperance_vie"].max())
        ) / 3
    else:
        df["IDH"] = np.nan

# Score vulnérabilité
vuln_cols = [
    "mortalite_adulte",
    "deces_nourrissons",
    "deces_moins_5_ans",
    "mortalite_vih_sida",
    "maigreur_1_19_ans",
    "maigreur_5_9_ans"
]
df["vulnerabilite"] = df[vuln_cols].fillna(0).mean(axis=1)

# ================================
# 🔹 Layout
# ================================
layout = dbc.Container([

    html.H2(" Dashboard Santé & IDH", className="mb-4"),

    dbc.Row([
        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.H4("IDH moyen"),
                html.H2(id="kpi_idh_moyen")
            ])
        ], class_name="mb-3")),
        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.H4("Espérance de vie moyenne"),
                html.H2(id="kpi_ev_moyenne")
            ])
        ], class_name="mb-3")),
        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.H4("Vulnérabilité moyenne"),
                html.H2(id="kpi_vuln_moyenne")
            ])
        ], class_name="mb-3")),
    ]),

    html.Hr(),

    dbc.Row([
        dbc.Col([
            html.Label("Filtrer par statut :"),
            dcc.Dropdown(
                id="filter_statut",
                options=[{"label": s, "value": s} for s in sorted(df["statut"].dropna().unique())],
                value=sorted(df["statut"].dropna().unique()),
                multi=True
            )
        ], width=4),
    ], class_name="mb-2"),

    dbc.Row([
        dbc.Col(dcc.Graph(id="graph_idh"), width=12),
    ]),

    html.Hr(),

    dbc.Row([
        dbc.Col(dcc.Graph(id="graph_vuln"), width=12),
    ]),

    html.Hr(),

    dbc.Row([
        dbc.Col(dcc.Graph(id="graph_corr"), width=12),
    ]),
], fluid=True)


# ================================
# 🔹 Callbacks
# ================================


# ✅ KPI
@dash.callback(
    Output("kpi_idh_moyen", "children"),
    Output("kpi_ev_moyenne", "children"),
    Output("kpi_vuln_moyenne", "children"),
    Input("filter_statut", "value")
)
def update_kpis(statuts):
    dff = df[df["statut"].isin(statuts)] if statuts else df
    return (
        f"{dff['IDH'].mean():.2f}",
        f"{dff['esperance_vie'].mean():.1f} ans",
        f"{dff['vulnerabilite'].mean():.2f}"
    )


# ✅ Scatter IDH vs espérance de vie
@dash.callback(
    Output("graph_idh", "figure"),
    Input("filter_statut", "value"),
)
def update_graph_idh(statuts):
    dff = df[df["statut"].isin(statuts)] if statuts else df

    fig = px.scatter(
        dff,
        x="esperance_vie",
        y="IDH",
        color="statut",
        trendline="ols",
        opacity=0.7
    )
    fig.update_layout(
        title="Relation entre Espérance de vie et IDH",
        xaxis_title="Espérance de vie",
        yaxis_title="IDH",
        template="plotly_dark"
    )
    return fig


# ✅ Vulnérabilité par statut
@dash.callback(
    Output("graph_vuln", "figure"),
    Input("filter_statut", "value"),
)
def update_graph_vuln(statuts):
    dff = df[df["statut"].isin(statuts)] if statuts else df

    fig = px.box(
        dff,
        x="statut",
        y="vulnerabilite",
        color="statut",
    )
    fig.update_layout(
        title="Distribution de la vulnérabilité sanitaire par statut",
        template="plotly_dark"
    )
    return fig


# ✅ Matrice de corrélation
@dash.callback(
    Output("graph_corr", "figure"),
    Input("filter_statut", "value"),
)
def update_corr(statuts):
    dff = df[df["statut"].isin(statuts)] if statuts else df

    corr = dff[[
        "esperance_vie", "IDH",
        "mortalite_adulte", "deces_nourrissons",
        "deces_moins_5_ans", "mortalite_vih_sida",
        "maigreur_1_19_ans", "maigreur_5_9_ans"
    ]].corr()

    fig = px.imshow(
        corr,
        text_auto=True,
        color_continuous_scale="RdBu_r",
        zmin=-1, zmax=1
    )
    fig.update_layout(
        title="Matrice de corrélation des indicateurs de santé",
        template="plotly_dark"
    )
    return fig
