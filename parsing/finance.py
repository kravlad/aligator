import time
import json
import asyncio
import requests
import xmltodict
# import yfinance as yf
from datetime import datetime, timedelta

import config as cfg
from defs import summ_chan, bm, dec_place, sending, opsp_chan, get_balls

user_agent_headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}

yurl = 'http://query2.finance.yahoo.com/v8/finance/chart/{}?range=5d&interval=1d'

tickers = {
    'cbr-xml-daily': {
            'currencies': 
                ['USD', 'EUR', 'GBP', 'CNY']},  
    'cbr': {
            'metals': {
                'Золото': [4,0],
                'Серебро': [5,1],
                'Платина': [6,2],
                'Палладий': [7,3],
        }},        
    'yahoo': {
        'commodities': {
                    'Brent': 'BZ=F',
                    'Gas': 'NG=F'
        },
        'indices': {
                    'ММВБ': 'IMOEX.ME',
                    'RTS': 'GOOG', # no hist data
                    'S&P 500': '%5EGSPC',
                    'Dow Jones': '%5EDJI',
                    'Nasdaq': '%5EIXIC',
                    'FTSE': '%5EFTSE'
        },
        'crypto': {
            'BTC': 'BTC-USD',
            'ETH': 'ETH-USD'
    },
        'tmp': {'EURUSD': 'EURUSD=X'}
    }
}

data = {
    'currencies': {'heads': ['Курсы ЦБ РФ','','₽','₽'], 'max_len': 0, 'values': {}},
    'metals': {'heads': ['Драгоценные металлы','','₽','%'], 'max_len': 0, 'values': {}},
    'commodities': {'heads': ['Товары'], 'max_len': 0, 'values': {}},
    'indices': {'heads': ['Индексы','','','%'], 'max_len': 0, 'values': {}},
    'crypto': {'heads': ['Крипто','$','','%'], 'max_len': 0, 'values': {}},
    'Brent': {'heads': ['','$','','%'], 'max_len': 0, 'values': None},
    'Gas': {'heads': ['','€','','%'], 'max_len': 0, 'values': None},
    'tmp': {'heads': ['','€','','%'], 'max_len': 0, 'values': {}}
}


async def making(data):
    msg = ''
    for i in data:
        if data[i].get('values'):
            title = '<pre>{}</pre>'.format(data[i]['heads'][0])
            msg = f'{msg}\n{title}:\n'
            for k in data[i]['values']:
                obj = data[i]['values'][k]
                sign = await get_balls(obj['dif'])
                length = data[i]['max_len'] - obj['len'] + len(k)
                msg = '{}{}<pre>{} {}{}{} ({}{})</pre>\n'.format(msg, sign, k.ljust(length, ' '), data.get(k, data[i])['heads'][1], obj['str_val'], data.get(k, data[i])['heads'][2], obj['str_dif'], data.get(k, data[i])['heads'][3])
    
    head = 'cbr.ru / yahoo.com | #финансы'
    msg = f'{head}\n{msg}\n{head}'
    
    return [msg]

async def parsing_finance(nothing):   
    for t in range(2):
        r = requests.get('https://www.cbr-xml-daily.ru/daily_json.js')
        if r.status_code != 502:
            break
        await asyncio.sleep(3)
    
    content = json.loads(r.text)
    l = 0
    for i in tickers['cbr-xml-daily']['currencies']:
        val = content['Valute'][i]['Value']
        pr_val = content['Valute'][i]['Previous']
        dif = round(val - pr_val, 2)
        str_val = await dec_place(round(val, 2))
        str_dif = await dec_place(dif)
        length = len(i) + len(str_val)
        data['currencies']['values'][i] = {
            'str_val': str_val,
            'dif': dif,
            'str_dif': str_dif,
            'len': length
        }
        
        l = max(length, l)
    data['currencies']['max_len'] = l
    
    date = datetime.now()
    today = date.strftime('%d/%m/%Y')
    yesterday = (date - timedelta(hours=24)).strftime('%d/%m/%Y')

    url = f'https://www.cbr.ru/scripts/xml_metall.asp?date_req1={yesterday}&date_req2={today}'
    for t in range(2):
        r = requests.get(url)
        if r.status_code != 502:
            break
        await asyncio.sleep(3)

    content = xmltodict.parse(r.text)
    full = len(content['Metall']['Record']) > 4
    
    l = 0
    for i in tickers['cbr']['metals']:
        k = tickers['cbr']['metals'][i][0]
        j = tickers['cbr']['metals'][i][1]
        
        pr_val = float(content['Metall']['Record'][j]['Buy'].replace(',', '.'))
        if full:
            val = float(content['Metall']['Record'][k]['Buy'].replace(',', '.'))
        else:
            val = pr_val
        dif = round(val - pr_val, 2)
        perc = round((val - pr_val) / pr_val * 100, 2)
        str_val = await dec_place(round(val, 2))
        str_perc = await dec_place(perc)
        length = len(i) + len(str_val)
        data['metals']['values'][i] = {
            'str_val': str_val,
            'dif': dif,
            'str_dif': str_perc,
            'len': length
        }
        l = max(length, l)
    data['metals']['max_len'] = l

    for i in tickers['yahoo']:
        l = 0
        for k in tickers['yahoo'][i]:
            ticker = tickers['yahoo'][i][k]
            url = yurl.format(ticker)
            for t in range(2):
                r = requests.get(url=url, headers=user_agent_headers)
                if r.status_code != 502:
                    break
                await asyncio.sleep(3)
            
            content = json.loads(r.text)
            timestamps = content['chart']['result'][0]['timestamp']
            n = 0
            items = []
            for item in timestamps:
                value = content['chart']['result'][0]['indicators']['quote'][0]['close'][n]
                if value:
                    items.append({
                            'date': datetime.utcfromtimestamp(item),
                            'value': value if value else 1
                    })
                n += 1
                
            val = items[-2]['value']
            pr_val = items[-3]['value']
            diff = val - pr_val
            val = round(val, 2)
            str_val = await dec_place(val)
            dif = round(diff, 2)
            perc = round(diff / pr_val * 100, 2)
            str_perc = await dec_place(perc)
            
            length = len(k) + len(str_val)
            data[i]['values'][k] = {'val': val, 'pr_val': pr_val, 'str_val': str_val, 'dif': dif, 'str_dif': str_perc, 'len': length}
            
            l = max(length, l)
            await asyncio.sleep(3)
        data[i]['max_len'] = l
    
    ngf = data['commodities']['values']['Gas']
    eurusd = data['tmp']['values']['EURUSD']['val']
    val = ngf['val'] / 0.02802113521 / eurusd
    pr_val = ngf['pr_val'] / 0.02802113521 / eurusd
    # data['commodities']['values']['Gas']['val'] = val
    # data['commodities']['values']['Gas']['pr_val'] = pr_val

    r_val = round(val, 2)
    str_val = await dec_place(r_val)
    dif = round(val - pr_val, 2)
    perc = round((val - pr_val) / pr_val * 100, 2)
    str_perc = await dec_place(perc)
    length = len(str_val) + 3
    data['commodities']['values']['Gas'] = {'str_val': str_val, 'dif': dif, 'str_dif': str_perc, 'len': length}

    rts = await bm(src='finance')
    pr_val = rts['yahoo']['indices']['RTS']['close']
    
    url = yurl.format('RTSI.ME')
    r = requests.get(url=url, headers=user_agent_headers)
    content = json.loads(r.text)
    val = content['chart']['result'][0]['indicators']['quote'][0]['close'][0]
    
    rts['yahoo']['indices']['RTS'] = {'pr_close': pr_val, 'close': val}
    await bm(src='finance', data=rts)

    r_val = round(val, 2)
    str_val = await dec_place(r_val)
    dif = round(val - pr_val, 2)
    perc = round((val - pr_val) / pr_val * 100, 2)
    str_perc = await dec_place(perc)
    length = len(str_val) + 3
    data['indices']['values']['RTS'] = {'str_val': str_val, 'dif': dif, 'str_dif': str_perc, 'len': length}
    data.pop('tmp')

    msgs = await making(data)
    await sending(msgs,forward=opsp_chan)
