replacement = {'telegram': {
                    '<br></b>': '</b><br>',
                    '<br/></b>': '</b><br/>',
                    '<br>': '\n',
                    '<br/>': '\n',
                    '<br> ': '\n',
                    '<br/> ': '\n',
                    '\xa0': ' ',

                    'ДАННОЕ СООБЩЕНИЕ (МАТЕРИАЛ) СОЗДАНО И (ИЛИ) РАСПРОСТРАНЕНО ИНОСТРАННЫМ СРЕДСТВОМ МАССОВОЙ ИНФОРМАЦИИ, ВЫПОЛНЯЮЩИМ ФУНКЦИИ ИНОСТРАННОГО АГЕНТА, И (ИЛИ) РОССИЙСКИМ ЮРИДИЧЕСКИМ ЛИЦОМ, ВЫПОЛНЯЮЩИМ ФУНКЦИИ ИНОСТРАННОГО АГЕНТА.': '',
                    'ДАННОЕ СООБЩЕНИЕ (МАТЕРИАЛ) СОЗДАНО И (ИЛИ) РАСПРОСТРАНЕНО ИНОСТРАННЫМ СРЕДСТВОМ МАССОВОЙ ИНФОРМАЦИИ, ВЫПОЛНЯЮЩИМ ФУНКЦИИ ИНОСТРАННОГО АГЕНТА, И (ИЛИ) РОССИЙСКИМ ЮРИДИЧЕСКИМ ЛИЦОМ, ВЫПОЛНЯЮЩИМ ФУНКЦИИ ИНОСТРАННОГО АГЕНТА': '',
                    # 'ДАННОЕ СООБЩЕНИЕ (МАТЕРИАЛ) СОЗДАНОИ (ИЛИ) РАСПРОСТРАНЕНО ИНОСТРАННЫМ СРЕДСТВОМ МАССОВОЙ ИНФОРМАЦИИ, ВЫПОЛНЯЮЩИМ ФУНКЦИИ ИНОСТРАННОГО АГЕНТА, И(ИЛИ) РОССИЙСКИМ ЮРИДИЧЕСКИМ ЛИЦОМ, ВЫПОЛНЯЮЩИМ ФУНКЦИИ ИНОСТРАННОГО АГЕНТА.': '',
                    # 'ДАННОЕ СООБЩЕНИЕ (МАТЕРИАЛ) СОЗДАНОИ (ИЛИ) РАСПРОСТРАНЕНО ИНОСТРАННЫМ СРЕДСТВОМ МАССОВОЙ ИНФОРМАЦИИ, ВЫПОЛНЯЮЩИМ ФУНКЦИИ ИНОСТРАННОГО АГЕНТА, И(ИЛИ) РОССИЙСКИМ ЮРИДИЧЕСКИМ ЛИЦОМ, ВЫПОЛНЯЮЩИМ ФУНКЦИИ ИНОСТРАННОГО АГЕНТА': '',
                    '&nbsp;': ' ',
                    '\n \n': '\n\n',
                    '\n\n\n': '\n\n',
                    '\n \n\n': '\n\n',
                    '\n\n \n': '\n\n',
                    '\n\n\n': '\n\n',
                    '  ': ' '
}}

tickers = {
    'cbr-xml-daily':
        ['USD', 'EUR', 'GBP', 'CNY'],
    'cbr': {
        'Золото': [4, 0],
        'Серебро': [5, 1],
        'Платина': [6, 2],
        'Палладий': [7, 3],
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
                    'RTS': 'GOOG',  # no hist data
                    'S&P 500': '%5EGSPC',
                    'Dow Jones': '%5EDJI',
                    'Nasdaq': '%5EIXIC',
                    'FTSE': '%5EFTSE'
        }
        }
}


urls = {
    'telegram': 'https://t.me/',
    'finance': {
            'curs': 'https://www.cbr.ru/currency_base/daily/?UniDbQuery.Posted=True&UniDbQuery.To=',
            'mets': 'https://www.cbr.ru/hd_base/metall/metall_base_new/',
            'yahoo': 'https://finance.yahoo.com/quote/',
            'investing': 'https://ru.investing.com/'
    },
    'rbc': {
            'politic': 'https://www.rbc.ru/politics/',
            'business': 'https://www.rbc.ru/business/',
            'economy': 'https://www.rbc.ru/economics/',
            'finance': 'https://www.rbc.ru/finances/'
    },
    'calend': {
            'url': 'https://www.calend.ru',
            'chapts': {
                        'holidays': 'Праздники',
                        'thisDay': 'Также в этот день',
                        'events': 'События',
                        'births': 'В этот день родились',
                        'mourns': 'День памяти',
            }
    },
    
    'intermedia': {
        'website': 'https://www.intermedia.ru',
        'url': '/rubrics/1'
    },
    
    'kinonews': {
        'website': 'https://www.kinonews.ru',
        'url': '/news_p1/'
    }
}

tg_limits = {
    'msg_lim': 4096,
    'capt_lim': 1032,
    'entities': 100,
    'poll_abzac': 2
}


pips = {
    # 'telegram': '\n🔹',
    'kinonews': '🎬',
    'intermedia': '🎵',
    'holidays': '🎈',
    'thisDay': '⏳',
    'events': '📆',
    'births': '🎂',
    'mourns': '☠️',
    'd_code': ''

}
