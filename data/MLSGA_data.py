import requests
import pandas as pd
import os
from pathlib import Path
import time

Base = "https://v3.football.api-sports.io"
HEADERS = {
    'x-rapidapi-key': os.environ["API_KEY"],
    'x-rapidapi-host': 'v3.football.api-sports.io'
    }

def api_get(endpoint: str, params:dict):
    url = f"{Base}/{endpoint}"
    r = requests.get(url, headers=HEADERS,params=params, timeout=30)
    r.raise_for_status()
    return r.json()

def league_data(some_id, season):
    data = api_get("fixtures", {"league": some_id, "season": season})
    
    match = data.get("response", [])
    
    errors = data.get("errors")
    if errors:
        print(f"[API errors] league={some_id} season={season}: {errors}")
        return None

    match = data.get("response", [])
    if not match:
        print(f"[WARN] Empty response league={some_id} season={season}")
        return None

    print(f"Season: {season}")
    print(f"Number of matches returned: {len(match)}")
    m0 = match[0]
    print("Example:", m0["fixture"]["id"], m0["teams"]["home"]["name"], "vs", m0["teams"]["away"]["name"])


    df = pd.DataFrame([{
        'date': m['fixture']['date'],
        'id' : m['fixture']['id'],
        'referee' : m['fixture']['referee'],
        'home_team_id' : m['teams']['home']['id'],
        'away_team_id' : m['teams']['away']['id'],
        'home_team' : m['teams']['home']['name'],
        'away_team' : m['teams']['away']['name'],
        'home_goals' : m['goals']['home'],
        'away_goals' : m['goals']['away'],
    }for m in match])
    
    df = df.dropna(subset=["home_goals", "away_goals"])

    def outcome(hg, ag):
        if hg > ag: return 0
        if hg == ag: return 1
        return 2

    df['result'] = [outcome(hg,ag) for hg, ag in zip(df["home_goals"], df['away_goals'])]
    
    assert df.shape[0] > 0
    assert df["date"].notna().all()
    assert df["home_goals"].notna().all()
    assert df["away_goals"].notna().all()

    df["date"] = pd.to_datetime(df["date"], utc=True).dt.tz_convert(None)
    df = df.sort_values("date").drop_duplicates(subset=["id"])

    league_name = match[0]['league']['name']

    df["total_goals"] = df["home_goals"] + df["away_goals"]
    df["goal_diff"] = df["home_goals"] - df["away_goals"]
    
    df = add_stats_to_df(df)
    
    output_dir = Path("data")
    output_dir.mkdir(exist_ok=True)

    output_path = output_dir/f"{league_name}-{season}.csv"
    df.to_csv(output_path, index=False)
    print("Saving to:", output_path)
    return output_path


def get_fixture_stats(fixture_id: int, home_id: int, away_id : int):
    data = api_get("fixtures/statistics", {"fixture": fixture_id})
    resp = data.get("response", [])
    out = {"id": fixture_id}
    
    if len(resp) == 0:
        return out
    
    for block in resp:
        team_id = block['team']['id']
        
        if team_id == home_id:
            side = 'home'
        elif team_id == away_id:
            side = 'away'
        else:
            continue
            
        for s in block.get("statistics", []):
            key = s["type"].lower().replace(" ", "_").replace("-", "_")
            val = s["value"]
            out[f"{side}_{key}"] = val
            
    return out
        

def add_stats_to_df(df: pd.DataFrame):
    rows = []
    for _, r in df.iterrows():
        fid = int(r["id"])
        home_id = int(r["home_team_id"])
        away_id = int(r["away_team_id"])
        rows.append(get_fixture_stats(fid, home_id, away_id))
        
    stats_df = pd.DataFrame(rows)
    return df.merge(stats_df, on='id', how="left")


#league_id = [39, 79, 61, 140]
    """
    for league in league_id:
    for i in range(2022, 2024):
        output_path = league_data(league,i)
    """
if __name__ == "__main__":
    league_id = [39, 79, 61, 140]
    for league in league_id:
        for season in range(2022, 2025):  # 2022, 2023
            league_data(league, season)
            time.sleep(7)
