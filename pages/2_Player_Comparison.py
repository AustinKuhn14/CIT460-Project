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

st.title("Player Comparison")

logging.info(f"Player Comparison Selected")

if len(st.session_state.selected_players) < 2:
        st.info("Select at least 2 players to compare.")
elif len(st.session_state.selected_players) > 4:
     st.info("Drop a player to continue. Comparison MAX is 4 players")
else:
        df = load_data(st.session_state.selected_players, st.session_state.start_date,
        st.session_state.end_date)

        if df.empty:
            st.warning("No data found.")
            logging.warning("Query returned no results")
        else:
            st.subheader("Average Comparison")

            summary = df.groupby("player_name")[["pts","reb","ast"]].mean()

            best_pts = summary["pts"].idxmax()
            best_reb = summary["reb"].idxmax()
            best_ast = summary["ast"].idxmax()

            st.write(f"Best Scorer: {best_pts}")
            st.write(f"Best Rebounder: {best_reb}")
            st.write(f"Best Playmaker: {best_ast}")

            cols = st.columns(len(st.session_state.selected_players))

            for i, player in enumerate(st.session_state.selected_players):
                player_df = df[df["player_name"] == player]
                avg_pts = round(player_df["pts"].mean(), 1)
                avg_reb = round(player_df["reb"].mean(), 1)
                avg_ast = round(player_df["ast"].mean(), 1)

                cols[i].markdown(f"""
                    ### {player}
                    - **{avg_pts}** PPG  
                    - **{avg_reb}** RPG  
                    - **{avg_ast}** APG  
                    """)
                
            

            st.divider()

            # Graph comparison
            st.subheader("Points Comparison")

            fig, ax = plt.subplots()

            for player in st.session_state.selected_players:
                player_df = df[df["player_name"] == player]
                ax.plot(player_df["game_date"], player_df["pts"], label=player)

            ax.legend()
            plt.xticks(rotation=45)
            st.pyplot(fig)
