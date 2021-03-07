import baostock as bs
import utils as u
from stockClass import Stock
import pandas as pd

code = "sh.600000"
code_dict = {"sh.600000": {'code':'sh.600000', 'code_name':'浦发银行', 'ipoDate': "2000-01-01"}}
startdate = "2015-01-01"
enddate = "2016-01-01"

pd.set_option('mode.chained_assignment', None)
bs.login()
stock_dict = u.fetch_histkdata(stocks_dict = code_dict)
stock = Stock(code, dict_self=stock_dict[code])
buycnt, buysucc, avgmax, avgmin = stock.backtest(stock.strategy_macd_kdj_cci, 15, startdate, enddate)
print('buycnt, buysucc, avgmax, avgmin')
bs.logout()
