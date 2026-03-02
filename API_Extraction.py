#Purpose:
#Reads and pulls the API data from an imported NBA API
#Sprint: 1


#Need to install nba_api
from nba_api.stats.static import players
from nba_api.stats.endpoints import playergamelog
import time


def get_players():
    return players.get_active_players()


def get_GameLogs(player_id, season):
    try:
        gamelog = playergamelog.PlayerGameLog(
            player_id=player_id,
            season=season
        )
        df = gamelog.get_data_frames()[0]
        time.sleep(0.6)
        return df
    except Exception as e:
        print(f"Error getting player {player_id}: {e}")
        return None
    
   
# This shows how to call the live version of the API, however it may take too long to load which is why I switched
#   def get_GameLogs(player_id, season):
#     url = "https://stats.nba.com/stats/playergamelog"
#
#     params = {
#         "PlayerID": player_id,
#         "Season": season,
#         "SeasonType": "Regular Season"
#     }
#
#     headers = {
#         "User-Agent": "Mozilla/5.0",
#         "Referer": "https://www.nba.com/",
#         "Origin": "https://www.nba.com"
#     }
#
#     response = requests.get(url, headers=headers, params=params)
#     data = response.json()
#
#     columns = data["resultSets"][0]["headers"]
#     rows = data["resultSets"][0]["rowSet"]
#
#     df = pd.DataFrame(rows, columns=columns)
#
#     return df

#Same would be done for 
