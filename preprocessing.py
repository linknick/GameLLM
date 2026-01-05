import csv 
import pandas as pd
def make_subset(filename:str):
    with open(filename,encoding='utf-8') as f:
        df = pd.read_csv(f, index_col=0,nrows = 120) 
        df.to_csv(filename[:-4]+"Short.csv",index = False)
        
def split(filename:str):
    df = pd.read_csv(filename)
    games = []
    
    ban_col = [f"ban{i}" for i in range(1,6)]
    pick_col = [f"pick{i}" for i in range(1,6)]
    
    for i in range(0, len(df), 12):
        match_chunk = df.iloc[i:i+12]
        game_id = match_chunk["gameid"].iloc[0]
        patch = match_chunk["patch"].iloc[0]
        league = match_chunk["league"].iloc[0]
        
        team1 = match_chunk["side"].iloc[0]
        team2 = match_chunk["side"].iloc[5]
        posOfchamp = {match_chunk.iloc[i]["champion"]:match_chunk.iloc[i]["position"] for i in range(10)}
        team1_players = match_chunk[:5]
        team2_players = match_chunk[5:10]
        

        # 取第 11, 12 筆
        team1_bp = match_chunk.iloc[10][ban_col+pick_col+["result"]]
        team2_bp = match_chunk.iloc[11][ban_col+pick_col+["result"]]
        
        match_data = {
            "match_id": team1_bp.get("gameid", "unknown"),
            "team1": {
                "players": [{"position": match_chunk.iloc[i]["position"], "champion": match_chunk.iloc[i]["champion"]} for i in range(0,6)],
                "picks": [team1_bp[f"pick{i}"] for i in range(1,6)],
                "bans": [team1_bp[f"ban{i}"] for i in range(1,6)],
                "result": team1_bp["result"]
            },
            "team2": {
                "players": [{"position": match_chunk.iloc[i]["position"], "champion": match_chunk.iloc[i]["champion"]} for i in range(6,11)],
                "picks": [team2_bp[f"pick{i}"] for i in range(1,6)],
                "bans": [team2_bp[f"ban{i}"] for i in range(1,6)],
                "result": team2_bp["result"]
            }
        }

        
        games.append({
            "game_id": game_id,
            "patch": patch,
            "league": league,
            "team1": team1,
            "team2": team2,
            "winner": team1 if team1_bp["result"]==1 else team2,
            "team1_picks": match_data["team1"]["picks"],
            "team2_picks": match_data["team2"]["picks"],
            "team1_bans": match_data["team1"]["bans"],
            "team2_bans": match_data["team2"]["bans"]
        })
    
    games_df = pd.DataFrame(games)
    
    
    games_df.to_csv("games.csv", index=False)
    
    heroes = []

    for i in range(0, len(df), 12):
        match_chunk = df.iloc[i:i+12]
        game_id = match_chunk["gameid"].iloc[0]
        
        # Picks (前 10 筆)
        for j in range(10):
            row = match_chunk.iloc[j]
            heroes.append({
                "game_id": game_id,
                "team": row["side"],
                "role": row["position"],
                "champion": row["champion"],
                "is_pick": 1,
                "is_ban": 0,
                "result": row["result"]  # 1=win, 0=lose
            })
        
        # Bans (第 11、12 筆)
        for j in [10, 11]:
            row = match_chunk.iloc[j]
            bans = row[ban_cols]
            for b in bans:
                heroes.append({
                    "game_id": game_id,
                    "team": row["side"],
                    "role": None,
                    "champion": b,
                    "is_pick": 0,
                    "is_ban": 1,
                    "result": row["result"]
                })

    heroes_df = pd.DataFrame(heroes)
    heroes_df.to_csv("heroes.csv", index=False)


if __name__ == '__main__':
    ban_cols = ["ban" + str(i) for i in range(1,6)]
    split("match_data.csv")