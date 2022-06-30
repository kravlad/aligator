import os
# import json
# import configs.config as cfg

cwd = os.getcwd().split('/')[1]
hosting = True if cwd == 'var' else False

# with open('configs/config.json', 'r') as f:
#     file_cfg = json.load(f)

settings = {
    'token': os.environ.get('TOKEN'),
    'news_chan': os.environ.get('NEWS_CHAN'),
    'summ_chan': os.environ.get('SUMM_CHAN'),
    'opsp_chan': os.environ.get('OPSP_CHAN'),
    'log_chan': os.environ.get('LOG_CHAN'),
    'bm_path': os.environ.get('BM_PATH'),
    'tzone': os.environ.get('TZONE'),
    # 'file_cfg': file_cfg,
    # 'cfg': cfg,
    'hosting': hosting
}