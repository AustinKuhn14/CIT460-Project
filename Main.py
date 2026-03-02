#Purpose:
#This is the main file that will walk through all the steps of the pipe-to-pipe architecture
#Sprint: 1
#
#This project follows a Pipeline (Pipe‐and‐Filter) architectural style, where data flows through a sequence of independent processing stages:
#Extract → Transform → Load.
#
#Each stage acts as a “filter” that reads input, processes it, and passes output downstream. This modular design improves:
# Separation of concerns
# Testability
# Maintainability
# Reusability
#
#This approach is described in software architecture literature:
#Sallam, M. (2020). Fundamentals of Software Architecture —
#Chapter 11: Pipeline Architecture Style.
#https://medium.com/@mohamedsallam953/fundamental-of-software-architecture-chapter-11-pipeline-architecture-style-53e8bedefe14
from API_Extraction import get_players, get_GameLogs
from API_Clean import clean_GameLogs
from Insert import insert_GameLogs


def pipeline(season="2025-26"):
    players = get_players()

    for player in players:
        player_id = player["id"]
        player_name = player["full_name"]

        print(f"Getting {player_name}")

        df = get_GameLogs(player_id, season)
        clean_df = clean_GameLogs(df)

        if clean_df is not None:
            insert_GameLogs(clean_df, player_id, player_name)



if __name__ == "__main__":
    pipeline()