import requests
import time
import yfinance as yf
import json
import xmltodict

import config.config as cfg
import defs.common as common

async def get_fin():    
    head = 'finance'
    tmpDate = await common.get_time()
    
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

    data = {'cbr': {'curency': {}, 'metals': {'Золото': {}, 'Серебро': {}, 'Платина': {}, 'Палладий': {}, }}, 'yahoo': {'crypto': {}, 'commodities': {}, 'indices': {}}}
    
    r = requests.get('https://www.cbr-xml-daily.ru/daily_json.js')
    xxx = json.loads(r.text)
    
    for i in tickers['cbr-xml-daily']:
        val = xxx['Valute'][i]['Value']
        prval = xxx['Valute'][i]['Previous']
        dif = round(val - prval, 2)
        strval = await common.dec_place(round(val, 2))
        strdif = await common.dec_place(dif)
        llen = len(i) + len(strval)
        data['cbr']['curency'][i] = {
            'strval': strval,
            'dif': dif,
            'strdif': strdif,
            'len': llen
        }

    l = 'https://www.cbr.ru/scripts/xml_metall.asp?date_req1=' + str(tmpDate['mskylist'][2]).rjust(2, '0') + '/' + str(tmpDate['mskylist'][1]).rjust(2, '0') + '/' + str(tmpDate['mskylist'][0]) + '&date_req2=' + str(tmpDate['msklist'][2]).rjust(2, '0') + '/' + str(tmpDate['msklist'][1]).rjust(2, '0') + '/' + str(tmpDate['msklist'][0])
    # l = 'https://www.cbr.ru/scripts/xml_metall.asp?date_req1=10/06/2022&date_req2=11/06/2022'
    
    r = requests.get(l) # fix if holiday
    xxx = xmltodict.parse(r.text)
    
    for i in tickers['cbr']:
        k = tickers['cbr'][i][0]
        j = tickers['cbr'][i][1]
        
        val = float(xxx['Metall']['Record'][k]['Buy'].replace(',', '.'))
        prval = float(xxx['Metall']['Record'][j]['Buy'].replace(',', '.'))
        dif = round(val - prval, 2)
        perc = round((val - prval) / prval * 100, 2)
        strval = await common.dec_place(round(val, 2))
        strperc = await common.dec_place(perc)
        llen = len(i) + len(strval)
        data['cbr']['metals'][i] = {
            'strval': strval,
            'dif': dif,
            'strperc': strperc,
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
                prval = history.Close.values[-3]
                diff = last_close - prval
            else:
                if i == 'NG=F':
                    last_close = history.Close.values[-1] / 0.02802113521 / eurusd
                    prval = history.Close.values[-2] / 0.02802113521 / eurusd
                else:
                    last_close = history.Close.values[-1]
                    prval = history.Close.values[-2]
                diff = last_close - prval
            val = round(last_close, 2)
            strval = await common.dec_place(val)
            dif = round(diff, 2)
            perc = round(diff / prval * 100, 2)
            strperc = await common.dec_place(perc)
            
            x[i] = {'val': val, 'strval': strval, 'dif': dif, 'strperc': strperc}

    for i in tickers['yahoo']:
        for k in tickers['yahoo'][i]:
            data['yahoo'][i][k] = x[tickers['yahoo'][i][k]]
            data['yahoo'][i][k]['len'] = len(k) + len(data['yahoo'][i][k]['strval'])
    
    with open('parsing/files/finance.json', 'r') as f:
        rts = json.load(f)
    
    pr_close = rts['yahoo']['indices']['RTS']['close']
    close = yf.Ticker("RTSI.ME").info['previousClose']
    
    rts['yahoo']['indices']['RTS'] = {'pr_close': pr_close, 'close': close}
    with open('parsing/files/finance.json', 'w') as f:
        rts = json.dump(rts, f)
    
    val = round(close, 2)
    strval = await common.dec_place(val)
    dif = round(close - pr_close, 2)
    perc = round((close - pr_close) / pr_close * 100, 2)
    strperc = await common.dec_place(perc)
    llen = len(strval) + 3
    data['yahoo']['indices']['RTS'] = {'val': val, 'strval': strval, 'dif': dif, 'strperc': strperc, 'len': llen}
    return(head, data)


async def fin_parsing():
    x = await get_fin()
    head = x[0]
    data = x[1]
    tmpDate = await common.get_time()
    
    # определяем текст сообщения (заголовок и конец)
    headmsg = '<b>Котировки на сегодня:</b>\n' + tmpDate['msk_wd'] + ', ' + tmpDate['msk_date_tod'] + '\n'
    endmsg = '\nИсточник: cbr.ru | yahoo.com' + \
        '\n\n#<b>финансы</b> #cbr #yahoo #цбрф #банкроссии #инвестиции #котировки #биржа #сводка' + cfg.bot_msg_tail

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
        sign = await common.get_balls(obj['dif'])
        msg = msg + sign + '<pre>' + item + ' ' + obj['strval'] + ' ₽ (' + obj['strdif'] + ' ₽)</pre>\n'
    
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
    print(msgdata)
    return msgdata

if __name__ == "__main__":
    import asyncio
    asyncio.run(fin_parsing())