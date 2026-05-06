import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import sqlite3
import logging
import time
from datetime import datetime
from utils.Func import get_players, load_data

logging.basicConfig(
    filename="logs/app.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

if "selected_players" not in st.session_state:
    st.session_state.selected_players = []

if "start_date" not in st.session_state:
    st.session_state.start_date = None

if "end_date" not in st.session_state:
    st.session_state.end_date = None


player_list = get_players()

st.session_state.selected_players = st.sidebar.multiselect(
    "Select Players",
    player_list,
    default=st.session_state.selected_players
)

st.session_state.start_date = st.sidebar.date_input(
    "Start Date",
    value=st.session_state.start_date or datetime(2025, 10, 1)
)

st.session_state.end_date = st.sidebar.date_input(
    "End Date",
    value=st.session_state.end_date or datetime.today()
)
if st.session_state.start_date > st.session_state.end_date:
    st.sidebar.error("Start Date must be before End Date")



st.title("Player Overview")

logging.info(f"Dashboard Selected")

if len(st.session_state.selected_players) != 1:
    st.info("Select only 1 player to view.")
else:
    df = load_data(st.session_state.selected_players, st.session_state.start_date,
    st.session_state.end_date)

    if df.empty:
            st.warning("No data found.")
            logging.warning("Query returned no results")
    else:
            col1, col2, col3 = st.columns(3)
            col1.metric("Avg Points", round(df["pts"].mean(), 1))
            col2.metric("Avg Rebounds", round(df["reb"].mean(), 1))
            col3.metric("Avg Assists", round(df["ast"].mean(), 1))

            st.divider()

            st.subheader("Game Log")

            # Show table of games
            st.dataframe(
                df[["game_date", "pts", "reb", "ast", "matchup", "wl"]]
                .rename(columns={
                    "game_date": "Date",
                    "pts": "Points",
                    "reb": "Rebounds",
                    "ast": "Assists"
                }),
                use_container_width=True
            )

            # Pts Graph 
            st.subheader("Points Over Time")
            fig_pts, ax_pts = plt.subplots()
            ax_pts.plot(df["game_date"], df["pts"])
            ax_pts.axhline(df["pts"].mean(), linestyle='--')
            ax_pts.set_ylabel("Points")
            ax_pts.set_xlabel("Date")
            plt.xticks(rotation=45)
            st.pyplot(fig_pts)

            # Reb Graph
            st.subheader("Rebounds Over Time")
            fig_reb, ax_reb = plt.subplots()
            ax_reb.plot(df["game_date"], df["reb"])
            ax_reb.axhline(df["reb"].mean(), linestyle='--')
            ax_reb.set_ylabel("Rebounds")
            ax_reb.set_xlabel("Date")
            plt.xticks(rotation=45)
            st.pyplot(fig_reb)

            # Ast Graph
            st.subheader("Assists Over Time")
            fig_ast, ax_ast = plt.subplots()
            ax_ast.plot(df["game_date"], df["ast"])
            ax_ast.axhline(df["ast"].mean(), linestyle='--')
            ax_ast.set_ylabel("Assists")
            ax_ast.set_xlabel("Date")
            plt.xticks(rotation=45)
            st.pyplot(fig_ast)