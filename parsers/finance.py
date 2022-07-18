# import time
import json
import asyncio
import requests
import xmltodict
from datetime import datetime, timedelta

# import config as cfg
from defs import dec_place, sending, get_balls, envs, get_last

USER_AGENT_HEADER = {'User-Agent':
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}

yurl = 'http://query2.finance.yahoo.com/v8/finance/chart/{}?range=30d&interval=1d'

tickers = {
    'cbr': {
        'currencies':
        ['USD', 'EUR', 'GBP', 'CNY'],
            'metals': {
                'Золото': '1',
                'Серебро': '2',
                'Платина': '3',
                'Палладий': '4'
        }},
    'moex': {
        'indices': {
            'ММВБ': 'IMOEX',
                    'РТС': 'RTSI'
        }},
    'yahoo': {
        'commodities': {
            'Brent': 'BZ=F',
            'Gas': 'NG=F'
        },
        'indices': {
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
    'currencies': {'heads': ['Курсы ЦБ РФ', '', '₽', '₽'], 'max_len': 0, 'values': {}},
    'metals': {'heads': ['Драгоценные металлы', '', '₽', '%'], 'max_len': 0, 'values': {}},
    'commodities': {'heads': ['Товары'], 'max_len': 0, 'values': {}},
    'indices': {'heads': ['Индексы', '', '', '%'], 'max_len': 0, 'values': {}},
    'crypto': {'heads': ['Крипто', '$', '', '%'], 'max_len': 0, 'values': {}},
    'Brent': {'heads': ['', '$', '', '%'], 'max_len': 0, 'values': None},
    'Gas': {'heads': ['', '€', '', '%'], 'max_len': 0, 'values': None},
    'tmp': {'heads': ['', '€', '', '%'], 'max_len': 0, 'values': {}}
}


async def making(data):
    """docstring."""
    msg = ''
    for i in data:
        if data[i].get('values'):
            title = '<pre>{}</pre>'.format(data[i]['heads'][0])
            msg = f'{msg}\n{title}:\n'
            for k in data[i]['values']:
                obj = data[i]['values'][k]
                link = obj['link']
                ball = await get_balls(obj['dif'])
                sign = f'<a href="{link}">{ball}</a>'
                length = data[i]['max_len'] - obj['len'] + len(k)
                msg = '{}{}<pre>{} {}{}{} ({}{})</pre>\n'.format(msg, sign, k.ljust(length, ' '), data.get(k, data[i])[
                    'heads'][1], obj['str_val'], data.get(k, data[i])['heads'][2], obj['str_dif'], data.get(k, data[i])['heads'][3])

    head = 'cbr.ru / yahoo.com | #финансы'
    footer = envs['summ_footer']
    msg = f'{head}\n{msg}\n{head}\n@{footer}'

    return [msg]


async def parsing_finance(nothing):
    """docstring."""
    date = datetime.now()  # - timedelta(hours=(4*24))
    dates = {
        'val': date.strftime('%d.%m.%Y'),
        'pr_val': (date - timedelta(hours=24)).strftime('%d.%m.%Y')}
    values = {}
    for d in dates:
        url = 'http://www.cbr.ru/scripts/XML_daily.asp?date_req={}'.format(
            dates[d])
        for t in range(3):  # add checking the date
            r = requests.get(url)
            if r.status_code != 502:
                break
            await asyncio.sleep(3)

        content = xmltodict.parse(r.text)
        values[d] = {i['CharCode']: float((i['Value']).replace(
            ',', '.')) for i in content['ValCurs']['Valute']}
        if dates[d] != content['ValCurs']['@Date']:
            break

    l = 0
    for i in tickers['cbr']['currencies']:
        val = values['val'][i]
        if values.get('pr_val'):
            pr_val = values['pr_val'][i]
        else:
            pr_val = val
        dif = round(val - pr_val, 2)
        str_val = await dec_place(round(val, 2))
        str_dif = await dec_place(dif)
        length = len(i) + len(str_val)
        data['currencies']['values'][i] = {
            'str_val': str_val,
            'dif': dif,
            'str_dif': str_dif,
            'len': length,
            'link': 'https://www.cbr.ru/currency_base/daily/?UniDbQuery.Posted=True&UniDbQuery.To={}'.format(dates['val'])
        }

        l = max(length, l)
    data['currencies']['max_len'] = l

    date1 = (date - timedelta(weeks=2)).strftime('%d/%m/%Y')
    date2 = date.strftime('%d/%m/%Y')

    url = f'https://www.cbr.ru/scripts/xml_metall.asp?date_req1={date1}&date_req2={date2}'
    for t in range(3):
        r = requests.get(url)
        if r.status_code != 502:
            break
        await asyncio.sleep(3)

    content = xmltodict.parse(r.text)
    metals = content['Metall']['Record']
    values = {}
    for i in metals:
        item = i['@Code']
        if not values.get(item):
            values[item] = {}
        values[item][i['@Date']] = i['Buy']

    l = 0
    for i in tickers['cbr']['metals']:
        t = tickers['cbr']['metals'][i]

        val = await get_last(values[t], date, '%d.%m.%Y')
        pr_val = await get_last(values[t], (date - timedelta(hours=24)), '%d.%m.%Y')

        val = float(val.replace(',', '.'))
        pr_val = float(pr_val.replace(',', '.'))
        dif = round(val - pr_val, 2)
        perc = round((val - pr_val) / pr_val * 100, 2)
        str_val = await dec_place(round(val, 2))
        str_perc = await dec_place(perc)
        length = len(i) + len(str_val)
        data['metals']['values'][i] = {
            'str_val': str_val,
            'dif': dif,
            'str_dif': str_perc,
            'len': length,
            'link': 'https://www.cbr.ru/hd_base/metall/metall_base_new'
        }
        l = max(length, l)
    data['metals']['max_len'] = l

    date1 = (date - timedelta(weeks=2)).strftime('%Y-%m-%d')
    date2 = date.strftime('%Y-%m-%d')
    for i in tickers['moex']['indices']:
        t = tickers['moex']['indices'][i]
        url = f'https://iss.moex.com/iss/history/engines/stock/markets/index/securities/{t}.json?from={date1}&till={date2}'
        for p in range(3):
            r = requests.get(url)
            if r.status_code != 502:
                break
            await asyncio.sleep(3)

        content = r.json()  # add checking the date
        values = {i[2]: i[5] for i in content['history']['data']}

        val = await get_last(values, (date - timedelta(hours=24)), '%Y-%m-%d')
        pr_val = await get_last(values, (date - timedelta(hours=48)), '%Y-%m-%d')

        dif = round(val - pr_val, 2)
        perc = round((val - pr_val) / pr_val * 100, 2)
        str_val = await dec_place(round(val, 2))
        str_perc = await dec_place(perc)
        length = len(i) + len(str_val)
        data['indices']['values'][i] = {
            'str_val': str_val,
            'dif': dif,
            'str_dif': str_perc,
            'len': length,
            'link': f'https://www.moex.com/ru/index/{t}'
        }

    date1 = date - timedelta(hours=24)
    date2 = date - timedelta(hours=48)

    for i in tickers['yahoo']:
        l = 0
        for k in tickers['yahoo'][i]:
            ticker = tickers['yahoo'][i][k]
            url = yurl.format(ticker)
            for t in range(3):
                r = requests.get(url=url, headers=USER_AGENT_HEADER)
                if r.status_code != 502:
                    break
                await asyncio.sleep(3)

            content = json.loads(r.text)
            timestamps = content['chart']['result'][0]['timestamp']
            # n = 0
            items = []
            dict_items = {}
            for n, item in enumerate(timestamps):
                value = content['chart']['result'][0]['indicators']['quote'][0]['close'][n]
                if value:
                    dd = datetime.utcfromtimestamp(item)
                    ddd = dd.strftime('%Y%m%d')
                    dict_items[ddd] = value
                    items.append({
                        'date': datetime.utcfromtimestamp(item),
                        'str_date': ddd,
                        'value': value if value else 1
                    })
                # n += 1

            val = await get_last(dict_items, date1)
            pr_val = await get_last(dict_items, date2)
            diff = val - pr_val
            val = round(val, 2)
            str_val = await dec_place(val)
            dif = round(diff, 2)
            perc = round(diff / pr_val * 100, 2)
            str_perc = await dec_place(perc)

            length = len(k) + len(str_val)
            data[i]['values'][k] = {'val': val,
                                    'pr_val': pr_val,
                                    'str_val': str_val,
                                    'dif': dif,
                                    'str_dif': str_perc,
                                    'len': length,
                                    'link': f'https://finance.yahoo.com/quote/{ticker}'
                                    }

            l = max(length, l)
            await asyncio.sleep(3)
        data[i]['max_len'] = l

    ngf = data['commodities']['values']['Gas']
    eurusd = data['tmp']['values']['EURUSD']['val']
    val = ngf['val'] / 0.02802113521 / eurusd

    r_val = round(val, 2)
    str_val = await dec_place(r_val)
    length = len(str_val) + 3
    data['commodities']['values']['Gas'].update(
        {'str_val': str_val, 'len': length})

    data.pop('tmp')

    msgs = await making(data)
    await sending(msgs, chat_id=envs['summ_chan'], forward=envs['opsp_chan'])
