import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import plotly.express as px
import pandas as pd
# from sqlalchemy import create_engine

# --------------------------------------------------
# Load DB Path + Connect
# --------------------------------------------------
# with open('database_path.txt', 'r') as file:
#     path = file.read().replace('\n', '')

# engine = create_engine(path)

# # --------------------------------------------------
# # Load main Bar Plot dataset
# # --------------------------------------------------
# query = """
# SELECT 
#     avg_factor_year,
#     num_games,
#     team,
#     year
# FROM avg_factor_team_season;
# """

# df = pd.read_sql(query, engine)
# df["year_str"] = df["year"].astype(str)

# teams = sorted(df["team"].unique())
# years = sorted(df["year"].unique())

# # --------------------------------------------------
# # Load Umpire Favor Table
# # --------------------------------------------------
# ump_query = """
# SELECT umpire, favor_by_ump_sum, num_games, team
# FROM ump_favor_by_team;
# """

# ump_all = pd.read_sql(ump_query, engine)
# ump_all["temp_team"] = ump_all["team"]

# # Make ALL TEAMS entry
# worst_all = ump_all.sort_values("favor_by_ump_sum", ascending=True)
# worst_all["temp_team"] = worst_all["team"]
# worst_all["team"] = "ALL TEAMS"
# worst_all = worst_all[ump_all.columns]

# ump_df = pd.concat([ump_all, worst_all], ignore_index=True)


# -------------------------------------------------
# READ IN DIRECTLY THE CSV
# -------------------------------------------------

df = pd.read_csv("avg_factor_team_season.csv")
ump_df = pd.read_csv('ump_df.csv')

df["year_str"] = df["year"].astype(str)

teams = sorted(df["team"].unique())
years = sorted(df["year"].unique())

# --------------------------------------------------
# DASH APP
# --------------------------------------------------
app = dash.Dash(__name__)

app.layout = html.Div([

    html.H1("Umpire Favor Factor per Team"),

    # --------------------------------------------------
    # Year Filter
    # --------------------------------------------------
    html.Div([
        html.Label("Select Years:"),
        dcc.Dropdown(
            id="year-filter",
            options=[{"label": str(y), "value": y} for y in years],
            value=years,  # all selected initially
            multi=True,
            style={"width": "40%"}
        )
    ], style={"padding": "10px"}),

    # --------------------------------------------------
    # BAR PLOT
    # --------------------------------------------------
    dcc.Graph(id="bar-plot"),

    # --------------------------------------------------
    # Sort Direction
    # --------------------------------------------------
    html.H2(id="ump-title"),

    html.Div([
        html.Label("Sort by:"),
        dcc.RadioItems(
            id="ump-sort-direction",
            options=[
                {"label": "Worst → Best (Screws my Team 😠)", "value": "ASC"},
                {"label": "Best → Worst (Helps my Team ☺️)", "value": "DESC"},
            ],
            value="ASC",
            inline=True,
            style={"padding": "6px"}
        )
    ], style={"padding": "10px"}),

    # --------------------------------------------------
    # Team Selector for Ump Table
    # --------------------------------------------------
    html.Div([
        html.Label("Select Team for Umpire Table:"),
        dcc.Dropdown(
            id="ump-team-dropdown",
            options=[{"label": t, "value": t} for t in teams] +
                    [{"label": "ALL TEAMS", "value": "ALL TEAMS"}],
            value="ALL TEAMS",
            clearable=False,
            style={"width": "40%"}
        )
    ], style={"padding": "10px"}),

    # --------------------------------------------------
    # Load More Button
    # --------------------------------------------------
    html.Button(
        "Load More",
        id="load-more-btn",
        n_clicks=0,
        style={"margin": "10px", "padding": "8px 16px"}
    ),

    dcc.Store(id="ump-row-limit", data=10),

    # --------------------------------------------------
    # Ump Table
    # --------------------------------------------------
    dash_table.DataTable(
        id="ump-table",
        columns=[],
        style_table={"overflowX": "auto"},
        style_header={"fontWeight": "bold"},
        style_cell={"textAlign": "center", "padding": "6px"},
        page_size=50
    )
])


# --------------------------------------------------
# CALLBACK: BAR PLOT (updated for year filtering)
# --------------------------------------------------
@app.callback(
    Output("bar-plot", "figure"),
    Input("ump-sort-direction", "value"),
    Input("year-filter", "value")
)
def update_bar(sort_dir, selected_years):

    if not selected_years:
        return px.bar(title="No years selected")

    # Filter df to selected years
    dff = df[df["year"].isin(selected_years)].copy()

    # Recalculate totals based only on selected years
    totals_all = (
        dff.groupby("team")["avg_factor_year"]
        .sum()
        .reset_index()
        .rename(columns={"avg_factor_year": "total"})
    )

    dff2 = dff.merge(totals_all, on="team").sort_values("total", ascending=False)

    team_order = dff2["team"].unique().tolist()
    year_order = sorted([str(y) for y in selected_years])

    # Positive-only annotation position
    pos_heights = (
        dff[dff["avg_factor_year"] > 0]
        .groupby("team")["avg_factor_year"]
        .sum()
        .reset_index()
        .rename(columns={"avg_factor_year": "position"})
    )

    totals = totals_all.merge(pos_heights, on="team", how="left").fillna(0)

    fig = px.bar(
        dff2,
        x="team",
        y="avg_factor_year",
        color="year_str",
        title="Average Favor Factor per Team (Filtered)",
        color_discrete_sequence=px.colors.sequential.Turbo_r[4:15],
        category_orders={
            "team": team_order,
            "year_str": year_order
        }
    )

    # Add annotations
    for _, row in totals.iterrows():
        fig.add_annotation(
            x=row["team"],
            y=row["position"],
            text=f"{row['total']:.2f}",
            showarrow=False,
            yshift=8,
            font=dict(size=13, color="black")
        )

    fig.add_hline(y=0, line_width=3, line_color="black")

    fig.update_layout(
        xaxis_title="Team",
        yaxis_title="Average Umpire Favor Factor",
        font=dict(size=16),
        legend_title_text="Year",
        margin=dict(l=80, r=40, t=90, b=80),
        xaxis_tickangle=-45
    )

    fig.update_traces(
        marker=dict(line=dict(width=0.5, color="black")),
        opacity=0.95
    )

    return fig


# --------------------------------------------------
# CALLBACK: Row Limit (Load More)
# --------------------------------------------------
@app.callback(
    Output("ump-row-limit", "data"),
    Input("load-more-btn", "n_clicks"),
    Input("ump-team-dropdown", "value"),
    State("ump-row-limit", "data"),
    prevent_initial_call=True
)
def update_row_limit(n_clicks, selected_team, current_limit):
    ctx = dash.callback_context
    if not ctx.triggered:
        raise PreventUpdate

    trigger = ctx.triggered[0]["prop_id"].split(".")[0]

    if trigger == "ump-team-dropdown":
        return 10

    if trigger == "load-more-btn":
        if current_limit is None:
            current_limit = 10
        return min(current_limit + 10, 50)

    return current_limit


# --------------------------------------------------
# CALLBACK: Umpire Table
# --------------------------------------------------
@app.callback(
    Output("ump-table", "data"),
    Output("ump-table", "columns"),
    Output("ump-title", "children"),
    Input("ump-team-dropdown", "value"),
    Input("ump-row-limit", "data"),
    Input("ump-sort-direction", "value")
)
def update_umpire_table(selected_team, row_limit, sort_dir):

    if row_limit is None:
        row_limit = 10

    dff = ump_df[ump_df["team"] == selected_team].copy()

    ascending = (sort_dir == "ASC")
    dff = dff.sort_values("favor_by_ump_sum", ascending=ascending)

    # Title emoji
    title = "😠" if sort_dir == "ASC" else "☺️"

    # ALL TEAMS includes temp_team column
    if selected_team == "ALL TEAMS":
        columns = [
            {"name": "Umpire", "id": "umpire"},
            {"name": "Team", "id": "temp_team"},
            {"name": "Favor Total", "id": "favor_by_ump_sum"},
            {"name": "Games", "id": "num_games"}
        ]
        dff = dff[["umpire", "temp_team", "favor_by_ump_sum", "num_games"]]

    else:
        columns = [
            {"name": "Umpire", "id": "umpire"},
            {"name": "Favor Total", "id": "favor_by_ump_sum"},
            {"name": "Games", "id": "num_games"}
        ]
        dff = dff[["umpire", "favor_by_ump_sum", "num_games"]]

    dff = dff.head(row_limit)

    return dff.to_dict("records"), columns, title


# --------------------------------------------------
# RUN APP
# --------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True)
