if __name__ == "__main__":
    from impdirs import insimpdirs
    insimpdirs()

from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import requests
import time

import config.config as cfg

# import pandas as pd # pip3 install pandas
# import openpyxl # pip3 install openpyxl

async def parse_ev(table):#Функция разбора таблицы с вопросом
    # res = pd.DataFrame()
    
    year = ''
    title = ''
    category = ''

    try:
        year = table.find('span', {'class': 'year'}).text
    except AttributeError:
        pass

    title = table.find('span', {'class': 'title'}).text

    try:
        category = table.find('div', {'class': 'link'}).text
    except AttributeError:
        pass

    x = {
        'year': year, 
        'title': title, 
        'category': category
    }
    # res=res.append(pd.DataFrame([[etype, year, title, category]], columns = ['type', 'date', 'title', 'category']), ignore_index=True)
    return x


async def parse_person(table):#Функция разбора таблицы с вопросом
    # res = pd.DataFrame()
    
    byear = ''
    dyear = ''
    title = ''
    category = ''

    byear = table.find('span', {'class': 'year'}).text
    try:
        dyear = table.find('span', {'class': 'year2'}).text
    except AttributeError:
        pass

    title = table.find('span', {'class': 'title'}).text

    # try:
    #     category = table.find('div', {'class': 'link'}).text
    # except AttributeError:
    #     pass
    if dyear == '':
        year = byear
    else:
        year = byear + ' - ' + dyear
    
    x = {
        'year': year, 
        'title': title, 
        'category': category
    }
    # res=res.append(pd.DataFrame([[etype, year, title, category]], columns = ['type', 'date', 'title', 'category']), ignore_index=True)
    return x


async def getcalendev():
    # result = pd.DataFrame()
    # table = []
    now = datetime.now() + timedelta(hours=10)
    date = now.strftime('%d.%m.%Y')
    wd = cfg.weekday[int(now.strftime('%w'))]

    date = str(now.strftime('%m')) + '-' + str(now.strftime('%d'))

    # Парсим события с calend.ru
    url = cfg.url_calend + cfg.holidays + '/' + date
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html.parser')

    #парсим праздики
    div_container = soup.find('div', class_='block holidays')
    data = {'holydays': {}}
    # Then search in that div_container for all p tags with class "hello"
    i = 0
    for ptag in div_container.find_all('li', class_='three-three'):
        res = await parse_ev(ptag)
        data['holydays'][i] = res
        # result = result.append(res, ignore_index=True)
        i += 1

    #парсим а также в этот день
    div_container = soup.find('div', class_='block thisDay')

    data['thisday'] = {}
    # Then search in that div_container for all p tags with class "hello"
    try:
        i = 0
        for ptag in div_container.find_all('li', class_='three-three'):
            res = await parse_ev(ptag)
            data['thisday'][i] = res
            i += 1
            # result = result.append(res, ignore_index=True)
    except:
        pass

    time.sleep(3)
    #парсим хронику
    url = cfg.url_calend + cfg.events + '/' + date
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html.parser')

    div_container = soup.find('ul', class_='itemsNet')
    
    data['events'] = {}
    # Then search in that div_container for all p tags with class "hello"
    i = 0
    for ptag in div_container.find_all('li', class_='three-three'):
        res = await parse_ev(ptag)
        data['events'][i] = res
        i += 1
        # result = result.append(res, ignore_index=True)

    return data


async def getcalendpers():
    # result = pd.DataFrame()
    # table = []
    now = datetime.now() + timedelta(hours=10)
    date = now.strftime('%d.%m.%Y')
    wd = cfg.weekday[int(now.strftime('%w'))]

    date = str(now.strftime('%m')) + '-' + str(now.strftime('%d'))

    time.sleep(3)
    #парсим ДР
    url = cfg.url_calend + cfg.persons + '/' + date
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html.parser')

    div_container = soup.find('ul', class_='itemsNet')

    data = {'born': {}}
    # Then search in that div_container for all p tags with class "hello"
    i = 0
    for ptag in div_container.find_all('li', class_='one-four birth'):
        res = await parse_person(ptag)
        data['born'][i] = res
        i += 1
        # result = result.append(res, ignore_index=True)

    time.sleep(3)
    #парсим годовщины
    url = cfg.url_calend + cfg.persons + '/' + date
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html.parser')

    div_container = soup.find('ul', class_='itemsNet')

    data['died'] = {}
    # Then search in that div_container for all p tags with class "hello"
    i = 0
    for ptag in div_container.find_all('li', class_='one-four mourn'):
        res = await parse_person(ptag)
        data['died'][i] = res
        i += 1
        # result = result.append(res, ignore_index=True)

    # result.to_excel('result.xlsx')
    return data


async def msgcalev():
    text = await getcalendev()
    now = datetime.now() + timedelta(hours=10)
    date = now.strftime('%d.%m.%Y')
    wd = cfg.weekday[int(now.strftime('%w'))]
    head = 'Calend Events'

    msg = '<b>Календарь событий на сегодня:</b>\n' + wd + ', ' + date + '\n\nПраздники:'
    for i in text['holydays']:
        msg = msg + '\n' + '📍<b>' + text['holydays'][i]['title'][:2].replace("<", "&lt;") + '</b>' + \
                                    text['holydays'][i]['title'][2:].replace("<", "&lt;")
    
    msg = msg + '\n\nЗнаменательные события:'
    for i in text['events']:
        msg = msg + '\n' + '📍' + text['events'][i]['year'] + ' ' + \
                                    text['events'][i]['title'].replace("<", "&lt;")
    
    msg = msg + '\n\nИсточник: calend.ru' + '\n\n#<b>календарь</b> #calend #праздники #сводка' + cfg.bot_msg_tail
    msgdata = {0: msg}
    
    # i = 0
    # while i < len(text['type']):
    #     if text['type'][i] == 'Thisday':
    #         msg = msg + '\n' + text['title'][i]
    #     i += 1
    return msgdata


async def msgcalpers():
    text = await getcalendpers()
    now = datetime.now() + timedelta(hours=10)
    date = now.strftime('%d.%m.%Y')
    wd = cfg.weekday[int(now.strftime('%w'))]
    head = 'Calend Persons'

    msg = '<b>Календарь событий на сегодня:</b>\n' + wd + ', ' + date + '\n\nВ этот день родились:'
    for i in text['born']:
        msg = msg + '\n' + '📍' + text['born'][i]['year'] + ' ' + \
                                    text['born'][i]['title'].replace("<", "&lt;")
    
    msg = msg + '\n\nДень памяти:'
    for i in text['died']:
        msg = msg + '\n' + '📍' + text['died'][i]['year'] + ' ' + \
                                    text['died'][i]['title'].replace("<", "&lt;")
    
    msg = msg + '\n\nИсточник: calend.ru' + '\n\n#<b>календарь</b> #calend #именины #сводка' + cfg.bot_msg_tail
    msgdata = {0: msg}
    return msgdata


if __name__ == "__main__":
    test = msgcalev()
    print(test)
