import requests
import pandas as pd
import os
import numpy as np
from pathlib import Path
import time


def league_data(some_id, season):
    url = "https://v3.football.api-sports.io/fixtures"

    query_string = {
        "league": some_id,         
        "season": season        
    }

    headers = {
    'x-rapidapi-key': 'eb12aee9fb1f5d338a47bf720c4a9dd5',
    'x-rapidapi-host': 'v3.football.api-sports.io'
    }

    response = requests.get(url, headers=headers, params=query_string)
    data = response.json()

    print("status:", response.status_code)
    print("errors:", data.get("errors"))
    print("message:", data.get("message"))
    print("results:", data.get("results"))
    print("paging:", data.get("paging"))

    match = data['response']

    print(f"Season: {season}")
    print(f"Number of matches returned: {len(match)}")
    print(f"Full API response (first 2 items): {match[:2]}")

    df = pd.DataFrame([{
        'date': m['fixture']['date'],
        'id' : m['fixture']['id'],
        'referee' : m['fixture']['referee'],
        'home_team' : m['teams']['home']['name'],
        'away_team' : m['teams']['away']['name'],
        'home_goals' : m['goals']['home'],
        'away_goals' : m['goals']['away'],
    }for m in match])

    df['result'] = df.apply(
        lambda row: 'home' if row['home_goals'] > row['away_goals'] 
        else 'away' if row['home_goals'] < row['away_goals'] 
        else 'draw',
        axis=1
    )   
    
    assert df.shape[0] > 0
    assert df["date"].notna().all()
    assert df["home_goals"].notna().all()
    assert df["away_goals"].notna().all()

    df["date"] = pd.to_datetime(df["date"], utc=True).dt.tz_convert(None)
    df = df.sort_values("date").drop_duplicates(subset=["id"])

    league_name = match[0]['league']['name']

    df["total_goals"] = df["home_goals"] + df["away_goals"]
    df["date"] = pd.to_datetime(df["date"])
    df["goal_diff"] = df["home_goals"] - df["away_goals"]
    
    df = df.sort_values(by=["date", "home_team"])

    home = df[["id", "date", "home_team", "away_team", "home_goals", "away_goals", "total_goals", "goal_diff"]].rename(columns ={
        "home_team": "team",
        "away_team": "opponent",
        "home_goals": "goals_for",
        "away_goals": "goals_against"
    })
    home["is_home"] = 1

    away = df[["id", "date", "away_team", "home_team", "away_goals", "home_goals", "total_goals", "goal_diff"]].rename(columns ={
        "away_team": "team",
        "home_team": "opponent",
        "away_goals": "goals_for",
        "home_goals": "goals_against"
    })
    away["is_home"] = 0
    
    team_df = pd.concat([home, away], ignore_index=True).sort_values(["team", "date"])
    
    team_df["points"] = np.select(
        [
            team_df["goals_for"] > team_df["goals_against"],
            team_df["goals_for"] == team_df["goals_against"],
            team_df["goals_for"] < team_df["goals_against"]
        ],
        [3, 1, 0],
        default=0
        )
    
    g_gf = team_df.groupby("team")["goals_for"].shift(1)
    g_pts = team_df.groupby("team")["points"].shift(1)

    team_df["gf_rolls_mean_5"] = g_gf.rolling(window=5, min_periods=1).mean()
    team_df["pts_rolls_sum_5"] = g_pts.rolling(window=5, min_periods=1).sum()
    roll_home = ["gf_rolls_mean_5", "pts_rolls_sum_5"]

    home_roll = team_df[["id", "team"] + roll_home].rename(columns={c: f"home_{c}" for c in roll_home}) 
    df = df.merge(home_roll, how="left", left_on=["id", "home_team"], right_on=["id", "team"]).drop(columns=["team"])
    away_feat = team_df[["id", "team"] + roll_home].rename(columns={c: f"away_{c}" for c in roll_home})
    df = df.merge(away_feat, how="left", left_on=["id", "away_team"], right_on=["id", "team"]).drop(columns=["team"])
    
    df["gf_roll5_mean_diff"]  = df["home_gf_rolls_mean_5"] - df["away_gf_rolls_mean_5"]
    df["pts_roll5_sum_diff"]  = df["home_pts_rolls_sum_5"] - df["away_pts_rolls_sum_5"]

    
    output_dir = Path("data")
    output_dir.mkdir(exist_ok=True)

    output_path = output_dir/f"{league_name}-{season}.csv"
    df.to_csv(output_path, index=False)
    print("Saving to:", output_path)
    return output_path

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