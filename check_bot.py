import requests

TOKEN = '8111627355:AAEOP-AzwPN17MAaUH_2Doel5bZxn0jXIPI'

url = f'https://api.telegram.org/bot{TOKEN}/getUpdates'

response = requests.get(url)
print(response.json())
