import requests
import pandas as pd
from openpyxl import load_workbook
from openpyxl.utils import get_column_letter
from openpyxl.styles import Alignment
import os


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

    match = data['response']

    print(f"Season: {season}")
    print(f"Number of matches returned: {len(match)}")
    print(f"Full API response (first 2 items): {match[:2]}")

    games_df = pd.DataFrame([{
        'date': m['fixture']['date'],
        'id' : m['fixture']['id'],
        'referee' : m['fixture']['referee'],
        'home_team' : m['teams']['home']['name'],
        'away_team' : m['teams']['away']['name'],
        'home_goal(s)' : m['goals']['home'],
        'away_goal(s)' : m['goals']['away'],
    }for m in match])

    games_df['result'] = games_df.apply(
        lambda row: 'home' if row['home_goal(s)'] > row['away_goal(s)'] 
        else 'away' if row['home_goal(s)'] < row['away_goal(s)'] 
        else 'draw',
        axis=1
    )

    league_name = match[0]['league']['name']

    output_dir = "D/output"

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    output_path = f"D:/output/{league_name}-{season}.xlsx"
    games_df.to_excel(output_path, index=False)
    return output_path

def file_adjust(output_path):
    wb = load_workbook(output_path)
    ws= wb.active

    for col_idx in range(1, ws.max_column + 1):
        col_letter = get_column_letter(col_idx)
        ws.column_dimensions[col_letter].width = 20

    for row in ws.iter_rows():
        for cell in row:
            cell.alignment = Alignment(horizontal='center', vertical='center')

    wb.save(output_path)

    print(f"{output_path} saved \n你个狗!你个狗！你个狗!你个狗！你个狗!你个狗你个狗!你个狗！你个狗!你个狗！你个狗!你个狗你个狗!你个狗！你个狗!你个狗！你个狗!你个狗你个狗!你个狗！你个狗!你个狗！你个狗!你个狗你个狗!你个狗！你个狗!你个狗！你个狗!你个狗你个狗!你个狗！你个狗!你个狗！你个狗!你个狗你个狗!你个狗！你个狗!你个狗！你个狗!你个狗你个狗!你个狗！你个狗!你个狗！你个狗!你个狗你个狗!你个狗！你个狗!你个狗！你个狗!你个狗你个狗!你个狗！你个狗!你个狗！你个狗!你个狗你个狗!你个狗！你个狗!你个狗！你个狗!你个狗你个狗!你个狗！你个狗!你个狗！你个狗!你个狗你个狗!你个狗！你个狗!你个狗！你个狗!你个狗你个狗!你个狗！你个狗!你个狗！你个狗!你个狗你个狗!你个狗！你个狗!你个狗！你个狗!你个狗！")

#calling functions
"""
league_id = [39, 79, 61, 140]

for league in league_id:
    for i in range(2021, 2024):
        output_path = league_data(league,i)
        file_adjust(output_path)
"""

