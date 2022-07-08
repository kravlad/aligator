import asyncio
# from apscheduler.schedulers.asyncio import AsyncIOScheduler # pip3 install apscheduler

from defs import bm, save_bm, news_chan, opsp_chan, summ_chan
from parsing.telegram import parsing_tg
from parsing.intermedia import parsing_intermedia
from parsing.kinonews import parsing_kinonews
from parsing.calend import parsing_calend
from parsing.rbc import parsing_rbc
from parsing.finance import parsing_finance

funcs = {
    'telegram': parsing_tg,
    'kinonews': parsing_kinonews,
    'intermedia': parsing_intermedia,
    'calend': parsing_calend,
    'rbc': parsing_rbc,
    'finance': parsing_finance,
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
    # test = {"parse": {"finance": []}}
    # test = {"parse": {"intermedia": []}}
    # test = {"parse": {"rbc": {
    #                     "finec": ["economy","finance"],
    #                     "business": ["business"],
    #                     "politic": ["politic"]
    #         }}}
    # test = {"parse": {"kinonews": []}}
    # test = {"parse": {"calend": []}}
    test = {"parse": {"telegram": {'sources': [
                                "meduzalive",
                                "svtvnews",
    #                             "theinsider",
    #                             "proektproekt",
    #                             "agentstvonews",
    #                             "istories_media",
    #                             "takiedela",
    #                             "thevillagemsk",
    #                             "mediazonalinks",
    #                             "tvrain",
    #                             "novaya_pishet",
                                # "tele_eve"
                                ], 'params': {'chat_id': news_chan, 'dayly_chat_id': summ_chan, 'dayly_frwd': opsp_chan}}}}
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
