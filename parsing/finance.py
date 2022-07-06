import time
import json
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
        'currencies': {'EURUSD': 'EURUSD=X'}
    }
}

spr = {
    'currencies': ['Курсы ЦБ РФ','','₽','₽'],
    'metals': ['Драгоценные металлы','','₽','%'],
    'crypto': ['Крипто','$','','%'],
    'commodities': ['Товары'],
    'indices': ['Индексы','','','%'],
    'Brent': ['','$','','%'],
    'Gas': ['','€','','%'],
}



async def making(data):
    msg = ''
    for i in data:
        title = spr[i][0]
        msg = f'{msg}\n{title}:\n'
        for k in data[i]:
            obj = data[i][k]
            sign = await get_balls(obj['dif'])
            msg = '{}{}<pre>{} {}{}{} ({}{})</pre>\n'.format(msg, sign, k, spr.get(k, spr[i])[1], obj['str_val'], spr.get(k, spr[i])[2], obj['str_dif'], spr.get(k, spr[i])[3])
    
    head = 'cbr.ru / yahoo.com | #финансы'
    msg = f'{head}\n{msg}\n{head}'
    
    
    
    
    
    
    
    
    
    # inds = {}
    # for i in data:
    #     for j in data[i]:
    #         ind = 0
    #         for k in data[i][j]:
    #             try:
    #                 ind = max(ind, data[i][j][k]['len'])
    #             except:
    #                 pass
    #         inds[j] = ind

    # msg = '\nКурсы ЦБ РФ:\n'
    # for item in ['USD', 'EUR', 'GBP', 'CNY']:
    #     obj = data['cbr']['curency'][item]
    #     sign = await get_balls(obj['dif'])
    #     msg = '{}{}<pre>{} {} ₽ ({} ₽)</pre>\n'.format(msg, sign, item, obj['str_val'], obj['str_dif'])
    
    # msg = msg + '\nДрагоценные металлы:\n'
    # for item in data['cbr']['metals']:
    #     obj = data['cbr']['metals'][item]
    #     sign = await get_balls(obj['dif'])
    #     ind = inds['metals'] - obj['len'] + len(item)
    #     msg = msg + sign + '<pre>' + item.ljust(ind, ' ') + ' ' + obj['str_val'] + ' ₽ (' + obj['str_perc'] + '%)</pre>\n'
        
    # curencies = {
    #     'Brent': ' $',
    #     'Gas': ' €'
    # }
    
    # msg = msg + '\nТовары:\n'
    # for item in data['yahoo']['commodities']:
    #     obj = data['yahoo']['commodities'][item]
    #     sign = await get_balls(obj['dif'])
    #     ind = inds['commodities'] - obj['len'] + len(item)
    #     msg = msg + sign + '<pre>' + item.ljust(ind, ' ') + curencies[item] + obj['str_val'] + ' (' + obj['str_perc'] + '%)</pre>\n'
        
    # msg = msg + '\nИндексы:\n'
    # for item in data['yahoo']['indices']:
    #     obj = data['yahoo']['indices'][item]
    #     sign = await get_balls(obj['dif'])
    #     ind = inds['indices'] - obj['len'] + len(item)
    #     msg = msg + sign + '<pre>' + item.ljust(ind, ' ') + ' ' + obj['str_val'] + ' (' + obj['str_perc'] + '%)</pre>\n'
        
    # msg = msg + '\nКрипто:\n'
    # for item in data['yahoo']['crypto']:
    #     obj = data['yahoo']['crypto'][item]
    #     sign = await get_balls(obj['dif'])
    #     ind = inds['crypto'] - obj['len'] + len(item)
    #     msg = msg + sign + '<pre>' + item.ljust(ind, ' ') + ' $' + obj['str_val'] + ' (' + obj['str_perc'] + '%)</pre>\n'
        
    return [msg]







async def parsing_finance(nothing):    
    head = 'finance'
    data = {'currencies': {}, 'metals': {'Золото': {}, 'Серебро': {}, 'Платина': {}, 'Палладий': {}}, 'crypto': {}, 'commodities': {}, 'indices': {}, 'currencies': {}}
    
    r = requests.get('https://www.cbr-xml-daily.ru/daily_json.js')
    content = json.loads(r.text)
    
    for i in tickers['cbr-xml-daily']['currencies']:
        val = content['Valute'][i]['Value']
        pr_val = content['Valute'][i]['Previous']
        dif = round(val - pr_val, 2)
        str_val = await dec_place(round(val, 2))
        str_dif = await dec_place(dif)
        llen = len(i) + len(str_val)
        data['currencies'][i] = {
            'str_val': str_val,
            'dif': dif,
            'str_dif': str_dif,
            'len': llen
        }
        
    date = datetime.now()
    today = date.strftime('%d/%m/%Y')
    yesterday = (date - timedelta(hours=24)).strftime('%d/%m/%Y')

    url = f'https://www.cbr.ru/scripts/xml_metall.asp?date_req1={yesterday}&date_req2={today}'
    # l = 'https://www.cbr.ru/scripts/xml_metall.asp?date_req1=10/06/2022&date_req2=11/06/2022'
    
    r = requests.get(url) # fix if holiday
    content = xmltodict.parse(r.text)
    
    full = len(content['Metall']['Record']) > 4
    
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
        llen = len(i) + len(str_val)
        data['metals'][i] = {
            'str_val': str_val,
            'dif': dif,
            'str_dif': str_perc,
            'len': llen
        }

    for i in tickers['yahoo']:
        for k in tickers['yahoo'][i]:
            ticker = tickers['yahoo'][i][k]
            url = yurl.format(ticker)
            r = requests.get(url=url, headers=user_agent_headers)
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
            
            llen = len(ticker) + len(str_val)
            data[i][k] = {'val': val, 'pr_val': pr_val, 'str_val': str_val, 'dif': dif, 'str_dif': str_perc, 'len': llen}

    ngf = data['commodities']['Gas']
    eurusd = data['currencies']['EURUSD']['val']
    val = ngf['val'] / 0.02802113521 / eurusd
    pr_val = ngf['pr_val'] / 0.02802113521 / eurusd
    data['commodities']['Gas']['val'] = val
    data['commodities']['Gas']['pr_val'] = pr_val

    with open('tmp/finance.json', 'r') as f:
        rts = json.load(f)
    
    pr_val = rts['yahoo']['indices']['RTS']['close']
    
    url = yurl.format('RTSI.ME')
    r = requests.get(url=url, headers=user_agent_headers)
    content = json.loads(r.text)
    val = content['chart']['result'][0]['indicators']['quote'][0]['close'][0]
    
    rts['yahoo']['indices']['RTS'] = {'pr_close': pr_val, 'close': val}
    with open('tmp/finance.json', 'w') as f:
        rts = json.dump(rts, f)
    
    val = round(val, 2)
    str_val = await dec_place(val)
    dif = round(val - pr_val, 2)
    perc = round((val - pr_val) / pr_val * 100, 2)
    str_perc = await dec_place(perc)
    llen = len(str_val) + 3
    data['indices']['RTS'] = {'str_val': str_val, 'dif': dif, 'str_dif': str_perc, 'len': llen}
    data['currencies'].pop('EURUSD')

    msgs = await making(data)
    await sending(msgs,forward=opsp_chan)
