#Purpose:
#This creates a basic web application that shows data from one player's last 10 games
#Sprint: 1
#To run use: python -m streamlit run App.py

import streamlit as st
import sqlite3
import pandas as pd


def get_connection():
    return sqlite3.connect("nba.db")


def get_player_data(player_name):
    conn = get_connection()

    query = """
        SELECT *
        FROM GameLogs
        WHERE player_name = ?
    """

    df = pd.read_sql(query, conn, params=(player_name,))
    conn.close()

    return df


st.title("NBA Player Game Logs")

player_name = st.text_input("Enter Player Name")

if player_name:
    df = get_player_data(player_name)

    if df.empty:
        st.write("No data found.")
    else:
        st.dataframe(df)