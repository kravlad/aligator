import requests
from datetime import datetime, timedelta
from bs4 import BeautifulSoup # pip3 install bs4

import config as cfg
from defs import bm, making, sending

async def parsing_rbc_business(nothing):
    source = 'rbc_business'
    bookmarks = await bm(src=source)
    last_id = bookmarks['bookmarks'][source]
    website = cfg.urls['rbc'][source]

    for k in range(2):
        r = requests.get(website)
        if r.status_code != 502:
            break
        await asyncio.sleep(3)
    
    soup = BeautifulSoup(r.content, 'html.parser')
    content = soup.find_all('span', itemprop='itemListElement')
    data = {source: {}}
    for i in content:
        n = int(i.contents[1].attrs['content']) * -1
        link = i.contents[3].attrs['content']
        item_id = link.split('/')[-1]
        if last_id != item_id:
            data[source][n] = {
                                'id': item_id,
                                'publish': True,
                                'link': link,
                                'html_text': i.contents[5].attrs['content']
            }
        else:
            break

    if len(data[source]) > 0:
        last_id = data[source][-1]['id']
        await bm(src=source, data={'date': str(datetime.now()), 'bookmarks': {source: last_id}})
    
        sorted_data = sorted(data[source].items(), key=lambda x: x[0])
        data[source] = dict(sorted_data)
        
        head = 'rbc.ru | #рбк | #бизнес'
        msgs = await making(data, head=head, header=False)
        await sending(msgs)





async def getrbcbusiness():
    # получаем id последней новости
    head = 'RBCbusiness'
    lId = db.find_doc('bookmarks', {'title': head}, False)['newid']

    # получаем данные с сайта
    url = cfg.urls[head]['url']
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html.parser')

    # парсим новости
    content = soup.find('div', class_='itemListElement')
    i = 0
    j = 0
    k = 0
    data = {}
    for item in content:  # берем каждую 3ю(?) запись
        if i % 2 != 0:
            if j % 2 == 0:
                # получаем ссылку
                link = item.find('meta', {'itemprop': 'url'}).attrs['content']
                code = link[-24:]  # получаем id

                # проверяем на соответсвиее id последней новости с предыдущего парсинга (чтобы не дублировались)
                if lId != code:
                    title = item.find(
                        'meta', {'itemprop': 'name'}).attrs['content']  # получаем содержание новости
                    data[k] = {'srcid': 2,
                            'source': head,
                            # 'round': rnd,
                            # 'N': n,
                            'id': code,
                            'text': title,
                            'link': link,
                            'date': datetime.now()
                            }  # записываем в бд
                    # db.ins_doc('news', data, False)
                    # n -= 1
                    k += 1
                else:
                    break  # выходим из цикла если эту новость уже парсили
            j += 1
        i += 1

    # записываем id последней новости в бд
    if j > 0:
        try:
            # newid = db.getsortitem('news', {'source': head, 'round': rnd}, [('_id', 1)])[
                # 'id']  # получаем id последней новсти
            newid = data[0]['id']
            doc = {'newid': newid, 'date': datetime.now()}
            db.upd_doc('bookmarks', {'title': head},
                    doc, False)  # записываем id в бд
        except:
            pass
    return(head, data)


async def msgrbcbusiness():
    # получаем время и дату
    tmpDate = await common.get_time()
    wd = tmpDate['msk_wd']
    date = tmpDate['msk_date_tod']

    # определяем текст сообщения (заголовок и конец)
    oldmsg = '<b>Новости бизнеса:</b>\n\n'
    newmsg = ''
    endmsg = '\nИсточник: rbc.ru' + \
        '\n\n#<b>бизнес</b> #rbc #рбк #сводка #новости' + cfg.bot_msg_tail
    lenmsg = 106  # кол-во сиволов начального сообщения

    # получаем данные из бд
    head, olddata = await getrbcbusiness()
    if not len(olddata):
        return
    
    msgdata = {}
    data = await common.sort_dict(olddata, 'key', '', True)

    # data = list(db.sort_doc('news', {'source': head}, [
    #             ('round', 1), ('N', 1)], True))

    # заполняем сообщение новотями из бд
    i = 0
    j = 4 # начинаем счет entities

    for item in data:
        msgitem = '📍' + '<b>' + \
            str(data[item]['text'])[:2].replace("<", "&lt;") + '</b>' + \
            str(data[item]['text'])[2:].replace("<", "&lt;") + \
            ' <a href="' + data[item]['link'] + '">читать</a>\n'
        newmsg = oldmsg + msgitem  # добавляем новость к уже имеющемуся сообщению
        # кол-во символов обновленного сообщения без символов разметки
        lenitem = len(str(data[item]['text'])) + 8
        lenmsg = lenmsg + lenitem
        if lenmsg >= cfg.tg_limits['msg_lim'] or j > cfg.tg_limits['entities']:  # проверяем не привышает ли обновленное сообщение лимит телеграм или кол-во entities 100
            # если превышает записываем сообщение в словарь и обнуляем новое сообщение и счетчик символов
            msgdata[i] = oldmsg
            oldmsg = msgitem
            lenmsg = lenitem
            i += 1
            j = 4 # сбрасываем entities
        else:
            oldmsg = newmsg
            j += 2

    # добавляем к последнему сообщению концовку и записываем в msgdata
    msg = oldmsg + endmsg
    msgdata[i] = msg

    # очищаем бд
    # db.del_doc('news', {'source': head}, True)
    return msgdata


if __name__ == "__main__":
    

    test = msgrbcbusiness()
    print(test)
