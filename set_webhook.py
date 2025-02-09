import requests

TOKEN = '8111627355:AAEOP-AzwPN17MAaUH_2Doel5bZxn0jXIPI'
WEBHOOK_URL = 'https://points-app.onrender.com/webhook'

url = f'https://api.telegram.org/bot{TOKEN}/setWebhook?url={WEBHOOK_URL}'

response = requests.post(url)
print(response.json())
