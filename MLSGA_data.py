import requests
import pandas as pd

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

