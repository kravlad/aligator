import json
import asyncio
# from apscheduler.schedulers.asyncio import AsyncIOScheduler # pip3 install apscheduler

from defs import send_telegram, bm, save_bm
from configs.storage import settings as sets
from parsing.telegram import parsing_tg
from parsing.kinonews import parsing_kinonews
# from parsing.finance import fin_parsing

funcs = {
    'telegram': parsing_tg,
    'kinonews': parsing_kinonews
}

def handler(event={}, context=None):
    if event.get('parse'):
        sources = event['parse'].keys()
        for src in sources:
            if funcs.get(src):
                func = funcs[src]
                arg = event['parse'][src]
                loop = asyncio.get_event_loop().run_until_complete
                loop(func(arg))

    elif event.get('get_bm'):
        for i in event['get_bm'].keys():
            data =  event['get_bm'][i]
            loop = asyncio.get_event_loop().run_until_complete
            loop(bm(i, data))
            
    elif event.get('save_bm'):
        for i in event['save_bm']:
            # confile = sets['file_cfg']['bm_path'][i]
            loop = asyncio.get_event_loop().run_until_complete
            loop(save_bm(i))


if __name__ == "__main__":
    test = {"parse": {
                    "kinonews": [],
        
                    # "telegram": [
                    #             "meduzalive",
    #                             "svtvnews",
    #                             "theinsider",
    #                             "proektproekt",
    #                             "agentstvonews",
    #                             "istories_media",
    #                             "takiedela",
    #                             "thevillagemsk",
    #                             "mediazonalinks",
    #                             "tvrain",
    #                             "novaya_pishet",
    #                             "tele_eve"
                                # ]
            }}
    # test = {
    #         "get_bm": {
    #             "telegram": {
    #                 "meduzalive": 63275,
    #                 "svtvnews": 10410
    #         }}}
    # test = {"save_bm": ["telegram"]}
    
    handler(test) # once local start
    
    
    # scheduler = AsyncIOScheduler()
    # scheduler.add_job(handler, "interval", kwargs={'event': test}, hours=3)
    # scheduler.start()
    
    # try:
    #     asyncio.get_event_loop().run_forever()

    # except (KeyboardInterrupt, SystemExit):
    #         pass
    
    # import asyncio
    # test = asyncio.run(parsing_kinonews('kinonews'))

    # print(test)
