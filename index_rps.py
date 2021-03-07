import baostock as bs
import pandas as pd
import numpy as np
from enum import IntEnum, auto
from datetime import datetime, timedelta
import baostock_structure
import utils as u
import tech_benchmark as tech
from baostock_structure import MY_BASIC

# current trade day
CURRENT_TRADEDAY = "2021-02-05"

lg = bs.login()
'''
stock_list = u.load_stock_from_csv()
stock_list_IPO_over_1_year = u.load_stock_IPO_above(stock_list, 365, CURRENT_TRADEDAY)
rps_120 = tech.rps(stock_list_IPO_over_1_year, CURRENT_TRADEDAY, -180)

cci_list = tech.cci(['sh.600223'], "2021-01-01", "2021-02-05")
print(cci_list[0])
print('len is', len(cci_list[0]))
exit()

rsi_list = tech.RSI(['sh.600223'], "2020-12-01", "2021-02-05")
print(rsi_list[0])
'''
#pd.set_option('display.max_rows',None)
kdj_list = tech.KDJ(['sh.600223'], "2020-11-01", "2021-02-05")
print(kdj_list[0])

#### log out ####
bs.logout()
