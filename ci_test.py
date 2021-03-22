import baostock as bs
from stockClass import Stock
from get_finance_data import get_stock_data_from_csvfile
import pandas as pd

code = "sh.600000"
csvPath = r"sh.600000.csv"
startdate = "2015-01-01"
enddate = "2016-01-01"

pd.set_option('mode.chained_assignment', None)
bs.login()

# fetch data from csv file
df = get_stock_data_from_csvfile(csvPath)
stock = Stock(code, data=df)
buycnt, buysucc, avgmax, avgmin = stock.backtest(stock.strategy_macd_kdj_cci, 15, startdate, enddate)
print(buycnt, buysucc, avgmax, avgmin)
bs.logout()
