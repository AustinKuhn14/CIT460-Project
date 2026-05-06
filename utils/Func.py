import streamlit as st
import sqlite3
import pandas as pd
import time


@st.cache_data
def get_players():
    conn = sqlite3.connect("nba.db")
    players_df = pd.read_sql("SELECT DISTINCT player_name FROM GameLogs", conn)
    conn.close()
    return players_df["player_name"].sort_values().tolist()


@st.cache_data
def load_data(players, start_date, end_date):
    try:
        conn = sqlite3.connect("nba.db")
        start = time.time()
        placeholders = ",".join("?" for _ in players)

        query = f"""
            SELECT player_name, game_date, pts, reb, ast, min, matchup, wl
            FROM GameLogs
            WHERE player_name IN ({placeholders})
        """

        df = pd.read_sql(query, conn, params=tuple(players))
        conn.close()
        
        if not df.empty:
            df["game_date"] = pd.to_datetime(df["game_date"], format="%b %d, %Y")
            df = df.sort_values(by="game_date", ascending=False)

            mask = (df["game_date"] >= pd.to_datetime(st.session_state.start_date)) & (df["game_date"] <= pd.to_datetime(st.session_state.end_date))
            df = df.loc[mask]

            df["game_date"] = df["game_date"].dt.date

            end = time.time()

        return df

    except:
        st.error("Failed to load data.")
        return pd.DataFrame()