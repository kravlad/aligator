import time
import json
import requests
import xmltodict
import yfinance as yf
from datetime import datetime, timedelta

import config as cfg
from defs import summ_chan, send_telegram, bm, dec_place

tickers = {
    'cbr-xml-daily': 
        ['USD', 'EUR', 'GBP', 'CNY'],  
    'cbr': {
        'Золото': [4,0],
        'Серебро': [5,1],
        'Платина': [6,2],
        'Палладий': [7,3],
        },        
    'yahoo': {
        'crypto': {
            'BTC': 'BTC-USD',
            'ETH': 'ETH-USD'
    },
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
        }
    }
}

async def parsing_finance(nothing):    
    head = 'finance'
    data = {'cbr': {'curency': {}, 'metals': {'Золото': {}, 'Серебро': {}, 'Платина': {}, 'Палладий': {}, }}, 'yahoo': {'crypto': {}, 'commodities': {}, 'indices': {}}}
    
    r = requests.get('https://www.cbr-xml-daily.ru/daily_json.js')
    content = json.loads(r.text)
    
    for i in tickers['cbr-xml-daily']:
        val = content['Valute'][i]['Value']
        pr_val = content['Valute'][i]['Previous']
        dif = round(val - pr_val, 2)
        str_val = await dec_place(round(val, 2))
        str_dif = await dec_place(dif)
        llen = len(i) + len(str_val)
        data['cbr']['curency'][i] = {
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
    
    for i in tickers['cbr']:
        k = tickers['cbr'][i][0]
        j = tickers['cbr'][i][1]
        
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
        data['cbr']['metals'][i] = {
            'strval': str_val,
            'dif': dif,
            'strperc': str_perc,
            'len': llen
        }

    t = 'EURUSD=X '
    for i in tickers['yahoo']:
        for k in tickers['yahoo'][i].values():
            t = t + k + ' '
    ytickers = yf.Tickers(t)
    list_tickers = t.split()

    x = {}
    # get stock info
    eurusd = ytickers.tickers['EURUSD=X'].history(period="1d").Close.values[-1] # check
    for i in list_tickers[1:]:
        history = ytickers.tickers[i].history(period="5d")
        if history.Close.empty:
            x[i] = {'close': ytickers.tickers[i].info['previousClose'], 'diff': 0}
        else:
            crypto = tickers['yahoo']['crypto'].values()
            if i in crypto:
                last_close = history.Close.values[-2]
                pr_val = history.Close.values[-3]
                diff = last_close - pr_val
            else:
                if i == 'NG=F':
                    last_close = history.Close.values[-1] / 0.02802113521 / eurusd
                    pr_val = history.Close.values[-2] / 0.02802113521 / eurusd
                else:
                    last_close = history.Close.values[-1]
                    pr_val = history.Close.values[-2]
                diff = last_close - pr_val
            val = round(last_close, 2)
            str_val = await dec_place(val)
            dif = round(diff, 2)
            perc = round(diff / pr_val * 100, 2)
            str_perc = await dec_place(perc)
            
            x[i] = {'val': val, 'str_val': str_val, 'dif': dif, 'strperc': str_perc}

    for i in tickers['yahoo']:
        for k in tickers['yahoo'][i]:
            data['yahoo'][i][k] = x[tickers['yahoo'][i][k]]
            data['yahoo'][i][k]['len'] = len(k) + len(data['yahoo'][i][k]['str_val'])
    
    with open('tmp/finance.json', 'r') as f:
        rts = json.load(f)
    
    pr_close = rts['yahoo']['indices']['RTS']['close']
    close = yf.Ticker("RTSI.ME").info['previousClose']
    
    rts['yahoo']['indices']['RTS'] = {'pr_close': pr_close, 'close': close}
    with open('tmp/finance.json', 'w') as f:
        rts = json.dump(rts, f)
    
    val = round(close, 2)
    str_val = await dec_place(val)
    dif = round(close - pr_close, 2)
    perc = round((close - pr_close) / pr_close * 100, 2)
    str_perc = await dec_place(perc)
    llen = len(str_val) + 3
    data['yahoo']['indices']['RTS'] = {'val': val, 'str_val': str_val, 'dif': dif, 'str_perc': str_perc, 'len': llen}
    return(head, data)


async def fin_parsing():
    inds = {}
    for i in data:
        for j in data[i]:
            ind = 0
            for k in data[i][j]:
                try:
                    ind = max(ind, data[i][j][k]['len'])
                except:
                    pass
            inds[j] = ind

    msg = headmsg + '\nКурсы ЦБ РФ:\n'
    for item in ['USD', 'EUR', 'GBP', 'CNY']:
        obj = data['cbr']['curency'][item]
        sign = await get_balls(obj['dif'])
        msg = '{}{}<pre>{} {} ₽ ({} ₽)</pre>\n'.format(msg, sign, item, obj['str_val'], obj['str_dif'])
    
    msg = msg + '\nДрагоценные металлы:\n'
    for item in data['cbr']['metals']:
        obj = data['cbr']['metals'][item]
        sign = await common.get_balls(obj['dif'])
        ind = inds['metals'] - obj['len'] + len(item)
        msg = msg + sign + '<pre>' + item.ljust(ind, ' ') + ' ' + obj['strval'] + ' ₽ (' + obj['strperc'] + '%)</pre>\n'
        
    curencies = {
        'Brent': ' $',
        'Gas': ' €'
    }
    
    msg = msg + '\nТовары:\n'
    for item in data['yahoo']['commodities']:
        obj = data['yahoo']['commodities'][item]
        sign = await common.get_balls(obj['dif'])
        ind = inds['commodities'] - obj['len'] + len(item)
        msg = msg + sign + '<pre>' + item.ljust(ind, ' ') + curencies[item] + obj['strval'] + ' (' + obj['strperc'] + '%)</pre>\n'
        
    msg = msg + '\nИндексы:\n'
    for item in data['yahoo']['indices']:
        obj = data['yahoo']['indices'][item]
        sign = await common.get_balls(obj['dif'])
        ind = inds['indices'] - obj['len'] + len(item)
        msg = msg + sign + '<pre>' + item.ljust(ind, ' ') + ' ' + obj['strval'] + ' (' + obj['strperc'] + '%)</pre>\n'
        
    msg = msg + '\nКрипто:\n'
    for item in data['yahoo']['crypto']:
        obj = data['yahoo']['crypto'][item]
        sign = await common.get_balls(obj['dif'])
        ind = inds['crypto'] - obj['len'] + len(item)
        msg = msg + sign + '<pre>' + item.ljust(ind, ' ') + ' $' + obj['strval'] + ' (' + obj['strperc'] + '%)</pre>\n'
        
    msg = msg + endmsg
    msgdata = {0: msg}
