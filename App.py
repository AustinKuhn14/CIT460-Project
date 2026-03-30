#Purpose:
# This module implements an interactive NBA analytics dashboard using Streamlit.
# It allows users to explore player performance through data visualization,
# compare multiple players, and generate probability-based predictions using
# historical game statistics. The application serves as the presentation layer
# of the ETL pipeline, transforming stored data into meaningful insights. 
#Sprint: 2
#To run use: python -m streamlit run App.py 

# This application still follows a pipeline (pipe-and-filter) architecture,
# where data flows through distinct stages: extraction, transformation,
# storage, and visualization. This part focuses on the visualization aspect allowing
# the user to access the data collected in a meaningful way.
# Based on:
# https://medium.com/@mohamedsallam953/fundamental-of-software-architecture-chapter-11-pipeline-architecture-style-53e8bedefe14


#Used Streamlit Documentation
#https://docs.streamlit.io/


import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import sqlite3
import logging
import time
from datetime import datetime

# Logging setup
logging.basicConfig(
    filename="logs/app.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


# Sidebar Menu
st.sidebar.title("NBA Analytics")
page = st.sidebar.radio("Navigation", ["Dashboard", "Player Comparison", "Predictions", "Last 5 Games"])

#Database
conn = sqlite3.connect("nba.db")

players_df = pd.read_sql("SELECT DISTINCT player_name FROM GameLogs", conn)
player_list = players_df["player_name"].sort_values().tolist()


#Filters For Sidebar Menu
st.sidebar.header("Filters")
selected_players = st.sidebar.multiselect("Select Players", player_list)

start_date = st.sidebar.date_input("Start Date", datetime(2025, 10, 1))
end_date = st.sidebar.date_input("End Date", datetime.today())

if start_date > end_date:
    st.sidebar.error("Start Date must be before End Date")

logging.info(f"Players: {selected_players}, Dates: {start_date} → {end_date}")

def load_data(players):
    try:
        start = time.time()
        placeholders = ",".join("?" for _ in players)

        query = f"""
            SELECT player_name, game_date, pts, reb, ast
            FROM GameLogs
            WHERE player_name IN ({placeholders})
        """

        df = pd.read_sql(query, conn, params=tuple(players))

        if not df.empty:
            df["game_date"] = pd.to_datetime(df["game_date"], format="%b %d, %Y")
            df = df.sort_values(by="game_date", ascending=False)

            mask = (df["game_date"] >= pd.to_datetime(start_date)) & (df["game_date"] <= pd.to_datetime(end_date))
            df = df.loc[mask]

            df["game_date"] = df["game_date"].dt.date

            end = time.time()
            process_time = round(end - start, 4)

            logging.info(f"Data Processing Time: {process_time}s")

        return df

    except Exception as e:
        logging.exception("Error when tring to load data")
        st.error("Failed to load data.")
        return pd.DataFrame()
    
#Main Dashboard
if page == "Dashboard":
    st.title("Player Overview")

    logging.info(f"Dashboard Selected")

    if len(selected_players) != 1:
        st.info("Select only 1 player to view.")
    else:
        df = load_data(selected_players)

        if df.empty:
            st.warning("No data found.")
            logging.warning("Query returned no results")
        else:
            col1, col2, col3 = st.columns(3)
            col1.metric("Avg Points", round(df["pts"].mean(), 1))
            col2.metric("Avg Rebounds", round(df["reb"].mean(), 1))
            col3.metric("Avg Assists", round(df["ast"].mean(), 1))

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

#Player Comparison
elif page == "Player Comparison":
    st.title("Player Comparison")

    logging.info(f"Player Comparison Selected")

    if len(selected_players) < 2:
        st.info("Select at least 2 players to compare.")
    else:
        df = load_data(selected_players)

        if df.empty:
            st.warning("No data found.")
            logging.warning("Query returned no results")
        else:
            st.subheader("Average Comparison")

            cols = st.columns(len(selected_players))

            for i, player in enumerate(selected_players):
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

            for player in selected_players:
                player_df = df[df["player_name"] == player]
                ax.plot(player_df["game_date"], player_df["pts"], label=player)

            ax.legend()
            plt.xticks(rotation=45)
            st.pyplot(fig)


# This applies principles of sports prediction using historical data,
# where past player performance is analyzed to estimate future outcomes.
# By examining trends such as points, rebounds, and assists over time,
# the system identifies patterns that can be used to calculate probabilities
# (e.g., likelihood of a player achieving a certain stat threshold).
#
# This approach aligns with modern sports analytics techniques, which rely on
# historical performance data to uncover patterns and inform predictions. 
# Right now it focuses more on Basic probability and may change to be more of Machine Learning
# in order to create something that is more predictive and more heavily weighed on recency.
#
# Based on concepts from:
# https://data-applied.com/blog/how-to-use-historical-data-to-predict-future-sports-outcomes

#Predictions
elif page == "Predictions":
    st.title("Player Performance Prediction")

    logging.info(f"Player Prediction Selected")

    if len(selected_players) != 1:
        st.info("Select exactly ONE player.")
    else:
        player = selected_players[0]

        df = load_data([player])

        if df.empty:
            st.warning("No data available.")
        else:
            st.subheader(f"Prediction for {player}")

            #Get input for desired stat
            stat_choice = st.selectbox("Select Stat", ["pts", "reb", "ast"])

            target_num = st.number_input(
                f"Enter target {stat_choice.upper()}",
                min_value=0,
                value=10
            )

            # Calculate Probability
            total_games = len(df)
            successful_games = len(df[df[stat_choice] >= target_num])

            probability = successful_games / total_games if total_games > 0 else 0

           
            st.metric("Games Analyzed", total_games)
            st.metric("Games Meeting Target", successful_games)

            st.success(
                f"{player} has a {round(probability * 100, 2)}% chance "
                f"of getting ≥ {target_num} {stat_choice.upper()}"
            )

            fig, ax = plt.subplots()

            ax.hist(df[stat_choice], bins=10)
            ax.axvline(target_num, linestyle="--")

            ax.set_title(f"{player} {stat_choice.upper()} Distribution")
            ax.set_xlabel(stat_choice.upper())
            ax.set_ylabel("Games Achieved")

            st.pyplot(fig)

#Other Analystics - Last 5 Games
elif page == "Last 5 Games":
    st.title("Stats for Last 5 Games")

    logging.info(f"Analytics for last 5 Games Selected")

    if len(selected_players) != 1:
        st.info("Select only 1 player to view.")
    else:
        df = load_data(selected_players)

        player = selected_players[0]

        df = load_data([player])

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


conn.close()