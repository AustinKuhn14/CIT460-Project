#Purpose:
# Filters the API to provide desired columns for database upload
#Sprint: 1

import pandas as pd

def clean_GameLogs(df):
    if df is None or df.empty:
        return None

    df.columns = df.columns.str.lower()

    df = df[[
        "game_id",
        "game_date",
        "matchup",
        "wl",
        "min",
        "pts",
        "reb",
        "ast"
    ]]

    return df