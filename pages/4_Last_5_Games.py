import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import sqlite3
import logging
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


st.title("Stats for Last 5 Games")

logging.info(f"Analytics for last 5 Games Selected")

if len(st.session_state.selected_players) != 1:
        st.info("Select only 1 player to view.")
else:

        player = st.session_state.selected_players[0]

        df = load_data([player], st.session_state.start_date,
        st.session_state.end_date)

        if df.empty:
            st.warning("No data available.")
            logging.warning("Query returned no results")
        else:
            st.subheader(f"Analysis of Last 5 Games for {player}")

            # Performance evaluation over last 5 games
            recent_avg = df.head(5)["pts"].mean()
            season_avg = df["pts"].mean()

            st.subheader("Performance Trend")

            col1, col2 = st.columns(2)
            col1.metric("Last 5 Games Avg", round(recent_avg, 1))
            col2.metric("Season Avg", round(season_avg, 1))

            if recent_avg > season_avg:
                st.success("Player is performing better than average")
            else:
                st.warning("Player is performing worse than average")

            st.divider()

            #Rolling Average Graph
            st.subheader("Rolling Average (5-Game Trend)")

            df_sorted = df.sort_values(by="game_date")

            df_sorted["rolling_pts"] = df_sorted["pts"].rolling(5).mean()

            fig_trend, ax_trend = plt.subplots()
            ax_trend.plot(df_sorted["game_date"], df_sorted["pts"], label="Actual")
            ax_trend.plot(
                df_sorted["game_date"],
                df_sorted["rolling_pts"],
                linestyle="--",
                label="5-Game Avg"
            )

            ax_trend.set_xlabel("Game Date")
            ax_trend.set_ylabel("Points")
            ax_trend.legend()
            plt.xticks(rotation=45)
            plt.tight_layout()

            st.pyplot(fig_trend)

            st.divider()

            # Consistency Score
            st.subheader("Consistency Analysis")

            consistency = df["pts"].std()

            st.metric("Consistency (Uses Std Dev - Lower is Better)", round(consistency, 2))

            st.caption("The lower the value the more consistent they are.")
