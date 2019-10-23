import os
import pandas as pd

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

DATA_DIR = BASE_DIR + '/data'


FUNDRAISING_MAP = {0: 'founding', 1: 'pre_seed', 2: 'seed', 3: 'series_a'}
PRE_SEED_VALUE = 10 #UPDATE
SEED_VALUE = 100 #UPDATE

FUNDING_HISTORY_INITIALIZER = pd.DataFrame.from_dict({FUNDRAISING_MAP[0]: [1, 0, 0.0, 0.0, 0.0, 0.0], FUNDRAISING_MAP[1]: [0, 1, 0, 0, 0, 0], FUNDRAISING_MAP[2]: [0, 2, 0, 0, 0, 0], FUNDRAISING_MAP[3]: [0, 3, 0, 0, 0, 0]}, orient = 'index', columns = ['active','round','pre_money','post_money','amt_raised','pct_sold'])
CAP_TABLE_INITIALIZER = pd.DataFrame.from_dict({FUNDRAISING_MAP[0]: [1, 0, 1.0, 0], FUNDRAISING_MAP[1]: [0, 1, 0, 0], FUNDRAISING_MAP[2]: [0, 2, 0, 0], FUNDRAISING_MAP[3]: [0, 3, 0, 0]}, orient = 'index', columns = ['active','round','pct_owned','value'])