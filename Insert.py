# Purpose:
# This module handles loading cleaned NBA data into SQLite.
# Sprint: 3

import sqlite3


def insert_GameLogs(df, player_id, player_name):

    conn = sqlite3.connect("nba.db")
    cursor = conn.cursor()

    # Create table if it doesn't exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS GameLogs (
            player_id INTEGER,
            player_name TEXT,
            game_id TEXT,
            game_date TEXT,
            matchup TEXT,
            wl TEXT,
            min INTEGER,
            pts INTEGER,
            reb INTEGER,
            ast INTEGER,
            UNIQUE(player_id, game_id)
        );
    """)

    # Insert rows
    for _, row in df.iterrows():
        cursor.execute("""
            INSERT INTO GameLogs
            (player_id, player_name, game_id, game_date, matchup, wl, min, pts, reb, ast)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT DO NOTHING
        """, (
            player_id,
            player_name,
            row["game_id"],
            row["game_date"],
            row["matchup"],
            row["wl"],
            row["min"],
            row["pts"],
            row["reb"],
            row["ast"]
        ))

    conn.commit()
    cursor.close()
    conn.close()