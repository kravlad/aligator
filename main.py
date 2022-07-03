import asyncio
# from apscheduler.schedulers.asyncio import AsyncIOScheduler # pip3 install apscheduler
# import json

from defs import bm, save_bm
from parsing.telegram import parsing_tg
from parsing.intermedia import parsing_intermedia
from parsing.kinonews import parsing_kinonews
from parsing.calend import parsing_calend
# from parsing.finance import fin_parsing
# from configs.storage import settings as sets

funcs = {
    'telegram': parsing_tg,
    'kinonews': parsing_kinonews,
    'intermedia': parsing_intermedia,
    'calend': parsing_calend,
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
    # test = {"parse": {"intermedia": []}}
    test = {"parse": {"kinonews": []}}
    # test = {"parse": {"calend": []}}
    # test = {"parse": {"telegram": [
    #                             "meduzalive",
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
                                # ]}}
    # test = {"get_bm": {"telegram": {
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
    
    # test = asyncio.run(parsing_kinonews([]))
