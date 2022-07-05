import requests
import json
from datetime import datetime
import yfinance as yf



user_agent_headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}

r = requests.get(url='http://query2.finance.yahoo.com/v8/finance/chart/aapl?range=5d&interval=1d',headers=user_agent_headers)
data = json.loads(r.text)

tss = data['chart']['result'][0]['timestamp']
xxx = {}
for i in tss:
    xxx[i] = datetime.fromtimestamp(i)

pass