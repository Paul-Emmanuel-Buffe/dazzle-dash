import dash
from dash import html, dcc, Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import pycountry

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
# ================================
#  Calcul des corrélations
# ================================

cols_corr = [
    "mortalite_adulte",
    "mortalite_vih_sida",
    "deces_moins_5_ans",
    "deces_nourrissons",
    "esperance_vie",
    'maigreur_1_19_ans',
    'maigreur_5_9_ans',
    "IDH"
]

# Filtrer uniquement les colonnes existantes (sécurité)
cols_corr = [c for c in cols_corr if c in df.columns]

corr_values = df[cols_corr].corr()["IDH"].sort_values(ascending=True)

df_corr = corr_values.reset_index()
df_corr.columns = ["indicateur", "correlation"]

fig_corr = px.bar(
    df_corr,
    x="correlation",
    y="indicateur",
    orientation="h",
    color="correlation",
    color_continuous_scale="RdBu",
    title="Corrélation entre indicateurs de santé et IDH"
)

fig_corr.update_layout(
    template="plotly_dark",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font_color="white",
    title_font_size=20
)
# =====================================================
#  Graphique : Evolution moyenne de l'espérance de vie par continent
# =====================================================

df_ev_continent = (
    df.groupby(['annee', 'continent'])['esperance_vie']
      .mean()
      .reset_index()
      .sort_values('annee')
)

fig_ev_continent = px.line(
    df_ev_continent,
    x="annee",
    y="esperance_vie",
    color="continent",
    markers=True,
    title="Évolution moyenne de l'espérance de vie par continent",
)

#  Mode sombre pour coller au style
fig_ev_continent.update_layout(
    template="plotly_dark",
    xaxis_title="Année",
    yaxis_title="Espérance de vie",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font_color="white",
    legend_title_text="Continent",
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

    # Section : Evolution espérance de vie par continent
    dbc.Row([
        dbc.Col(dcc.Graph(id="graph_ev_continent", figure=fig_ev_continent), width=12)
    ]),
    html.Hr(),

    dbc.Row([
        dbc.Col(
        dcc.Graph(id="graph_corr_indicateurs", figure=fig_corr),
        width=12
    )
    ]),
    html.Hr(),

    dbc.Row([
       dbc.Col(dcc.Graph(id="graph_vulnerabilite_map"), width=12),
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


#  KPI
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




# Fonction auxiliaire pour convertir les noms en ISO
def get_iso_code(country_name):
    try:
        return pycountry.countries.lookup(country_name).alpha_3
    except:
        return None

df["iso"] = df["pays"].apply(get_iso_code)

@dash.callback(
    Output("graph_vulnerabilite_map", "figure"),
    Input("filter_statut", "value")
)
def update_map(selected_status):
    # Normalisation des statuts
    df["statut_clean"] = df["statut"].str.strip().str.lower()
    selected_status = [s.lower() for s in selected_status]

    dff = df[df["statut_clean"].isin(selected_status)]

    # Sélection année — option : la dernière
    dff_latest = dff[dff["annee"] == dff["annee"].max()]

    # Sécurité : si vide
    if dff_latest.empty:
        return px.choropleth(title="Aucune donnée disponible")

    fig = px.choropleth(
        dff_latest,
        locations="iso",
        color="vulnerabilite",
        hover_name="pays",
        color_continuous_scale="Reds",
        title=f"Score de vulnérabilité par pays — Année {dff_latest['annee'].max()}",
    )
    fig.update_layout(template="plotly_dark")

    fig.update_geos(showcountries=True, showcoastlines=True)
    fig.update_layout(margin={"r":0,"t":40,"l":0,"b":0})

    return fig

#  Scatter IDH vs espérance de vie
@dash.callback(
    Output("graph_idh", "figure"),
    Input("filter_statut", "value"),
)
def update_graph_idh(statuts):
    dff = df[df["statut"].isin(statuts)] if statuts else df
    print(df["statut"].unique())


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




# correlation selon le sens de variation
@dash.callback(
    Output("graph_corr_indicateurs", "figure"),
    Input("filter_statut", "value")
)
def update_corr(selected_statut):
    df_filtre = df[df["statut"].isin(selected_statut)]

    corr_values = df_filtre[cols_corr].corr()["IDH"].sort_values(ascending=True)
    df_corr = corr_values.reset_index()
    df_corr.columns = ["indicateur", "correlation"]

    fig_corr = px.bar(
        df_corr,
        x="correlation",
        y="indicateur",
        orientation="h",
        color="correlation",
        color_continuous_scale="RdBu",
        title="Corrélation entre indicateurs de santé et IDH"
    )

    fig_corr.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", font_color="white")

    return fig_corr

# Vulnérabilité par statut
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


# Matrice de corrélation
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
