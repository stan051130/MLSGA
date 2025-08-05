import requests
import pandas as pd
from openpyxl import load_workbook
from openpyxl.utils import get_column_letter
from openpyxl.styles import Alignment

url = "https://v3.football.api-sports.io/fixtures"

query_string = {
    "league": "78",         
    "season": "2023"        
}

headers = {
  'x-rapidapi-key': 'eb12aee9fb1f5d338a47bf720c4a9dd5',
  'x-rapidapi-host': 'v3.football.api-sports.io'
}

response = requests.get(url, headers=headers, params=query_string)
data = response.json()

match = data['response']

games_df = pd.DataFrame([{
    'date': m['fixture']['date'],
    'id' : m['fixture']['id'],
    'referee' : m['fixture']['referee'],
    'home_team' : m['teams']['home']['name'],
    'away_team' : m['teams']['away']['name'],
    'home_goal(s)' : m['goals']['home'],
    'away_goal(s)' : m['goals']['away'],
    'result': m
}for m in match])

games_df['result'] = games_df.apply(
    lambda row: 'home' if row['home_goal(s)'] > row['away_goal(s)'] 
    else 'away' if row['home_goal(s)'] < row['away_goal(s)'] 
    else 'draw',
    axis=1
)

output_path = "D:/output/bundesliga2023-2024.xlsx"
games_df.to_excel(output_path, index=False)

wb = load_workbook(output_path)
ws= wb.active

for col_idx in range(1, ws.max_column + 1):
    col_letter = get_column_letter(col_idx)
    ws.column_dimensions[col_letter].width = 20

for row in ws.iter_rows():
    for cell in row:
        cell.alignment = Alignment(horizontal='center', vertical='center')

wb.save(output_path)

