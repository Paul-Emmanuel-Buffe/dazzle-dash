import dash
import dash_bootstrap_components as dbc
from dash import html, dcc

app = dash.Dash(
    __name__,
    use_pages=True,
    external_stylesheets=[dbc.themes.SLATE],  # Design pro
    suppress_callback_exceptions=True
)

# ================================
# 🔹 Navbar (header)
# ================================
navbar = dbc.Navbar(
    dbc.Container([
        dbc.Row([
            dbc.Col(html.H2("Dashboard Global - Groupe", style={"color": "white"})),
        ]),
    ]),
    color="primary",
    dark=True,
    className="mb-2",
)

# ================================
#  Sidebar (admin style)
# ================================
sidebar = html.Div(
    [
        html.H4("Navigation", className="text-white p-3"),
        html.Hr(style={"color": "white"}),
        dbc.Nav(
            [
                dbc.NavLink(" Accueil", href="/", active="exact", class_name="text-white"),
                dbc.NavLink(" Santé & IDH", href="/Sante_idh", active="exact", class_name="text-white"),
                dbc.NavLink(" Alimentation Mondiale", href="/Production alimentaire mondiale", active="exact", class_name="text-white"),
                dbc.NavLink(" Trafic Aérien", href="/Analyse du Trafic Aérien", active="exact", class_name="text-white"),    
            ],
            vertical=True,
            pills=True,
            class_name="p-3"
        ),
    ],
    style={
        "position": "fixed",
        "top": "70px",  # sous la navbar
        "bottom": "0",
        "left": "0",
        "width": "260px",
        "padding": "10px",
        "backgroundColor": "#2c3e50",
        "color": "white",
        "overflowY": "auto"
    },
)

# ================================
# 🔹 Layout principal
# ================================
app.layout = html.Div(
    [
        navbar,
        sidebar,
        html.Div(
            dash.page_container,
            style={
                "margin-left": "270px",
                "padding": "20px",
                "margin-top": "80px"
            }
        )
    ]
)

# ================================
# 🔹 Lancer l'app
# ================================
if __name__ == "__main__":
    app.run_server(debug=True)
