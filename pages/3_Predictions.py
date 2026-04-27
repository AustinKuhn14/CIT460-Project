import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import sqlite3
from sklearn.linear_model import LinearRegression
import numpy as np
from datetime import datetime
import logging
from sklearn.metrics import mean_absolute_error
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


st.title("Player Performance Prediction")

logging.info(f"Player Prediction Selected")

if len(st.session_state.selected_players) != 1:
        st.info("Select only 1 player to view.")
else:
        player = st.session_state.selected_players[0]

        df = load_data([player], st.session_state.start_date,
        st.session_state.end_date)

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

            if probability > 0.7:
                st.success("High chance of hitting target")
            elif probability > 0.45:
                st.warning("Moderate chance")
            else:
                st.error("Low chance of hitting target ")

            st.divider()


            # This prediction model applies principles of sports analytics where historical
            # player performance is used to estimate future outcomes. By analyzing past game
            # stats like points, rebounds, and assists, the model can identify trends
            # and patterns that can inform predictions. The model incorporates both
            # recent games and season averages, along with recency weighting to emphasize current player form.
            # Based on:
            # https://data-applied.com/blog/how-to-use-historical-data-to-predict-future-sports-outcomes

            # ML Model
            st.subheader("ML Prediction for Next Game")

            df = df.sort_values(by="game_date").reset_index(drop=True)

           # Create averages used for model prediction
            df["last_5_avg"] = df[stat_choice].rolling(5).mean()
            df["last_10_avg"] = df[stat_choice].rolling(10).mean()
            df["season_avg"] = df[stat_choice].expanding().mean()

            # Fill early null values
            df.fillna(method="bfill", inplace=True)

            # Define features that are being used for the model
            features = ["last_5_avg", "last_10_avg", "season_avg", "min"]

            X = df[features]
            y = df[stat_choice]
            #Weigh recent games more than older for recent performance.
            weights = np.linspace(1, 3, len(df))  
            

            # Train model
            model = LinearRegression()
            model.fit(X, y, sample_weight=weights)

            latest = df.iloc[-1]

            next_game = np.array([[
                latest["last_5_avg"],
                latest["last_10_avg"],
                latest["season_avg"],
                latest["min"]
            ]])

            prediction = model.predict(next_game)[0]

            st.metric(
                f"Predicted Next Game {stat_choice.upper()}",
                round(prediction)
            )

            

            split = int(len(df) * 0.8)

            X_train, X_test = X[:split], X[split:]
            y_train, y_test = y[:split], y[split:]

            model.fit(X_train, y_train)

            y_pred = model.predict(X_test)

            mae = mean_absolute_error(y_test, y_pred)

            st.metric(f"Model's Mean Absolute Error of {stat_choice.upper()}", round(mae, 2))
            st.divider()


            # Visualization of Prediction and Trend
            st.subheader("Trend + Prediction")

            fig, ax = plt.subplots()

            # Actual data
            ax.plot(df["game_date"], df[stat_choice], label="Actual")

            # Model trend
            ax.plot(df["game_date"], model.predict(X), linestyle="--", label="Trend")

            # Predict next game
            next_date = df["game_date"].iloc[-1] + pd.Timedelta(days=1)

            # Predicted point
            ax.scatter(next_date, prediction, label="Next Game Prediction")

            ax.set_xlabel("Game Date")
            ax.set_ylabel(stat_choice.upper())
            ax.legend()

            plt.xticks(rotation=45)
            plt.tight_layout()

            st.pyplot(fig)
