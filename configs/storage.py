import os
import json
import configs.config as cfg

with open('configs/config.json', 'r') as f:
    file_cfg = json.load(f)

settings = {
    'token': os.environ.get('TOKEN'),
    'news_chan': os.environ.get('NEWS_CHAN'),
    'summ_chan': os.environ.get('SUMM_CHAN'),
    'log_chan': os.environ.get('LOG_CHAN'),
    'file_cfg': file_cfg,
    'cfg': cfg
}