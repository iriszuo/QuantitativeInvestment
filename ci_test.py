import baostock as bs
from stockClass import Stock
from get_finance_data import get_stock_data_from_csvfile
from help_cal_bench import gain_dict_for_rps 
import pandas as pd

code = "sh.600000"
csvPath = r"sh.600000.csv"
startdate = "2015-01-01"
enddate = "2016-01-01"

if __name__ == '__main__':
    pd.set_option('mode.chained_assignment', None)
    bs.login()

    # fetch data from csv file and create stock instance
    df = get_stock_data_from_csvfile(csvPath)
    stock = Stock(code, data=df)

    # test backtest function, include macd, kdj, cci 
    buycnt, buysucc, avgmax, avgmin = stock.backtest(stock.strategy_macd_kdj_cci, 15, startdate, enddate)
    print("backtest done! --- ", buycnt, buysucc, avgmax, avgmin)
    
    # test rps
    # TODO: add stock list here
    dict_rps = gain_dict_for_rps(stock_list, enddate, 120)
    rps = stock.bench_RPS(dict_rps)
    print("rps test done! --- ", rps)
    
    # test rsi
    hisdata = stock.basic_period_hisdata(startdate, enddate)
    df = stock.bench_RSI(hisdata)
    print("rsi test done! --- ", df)

    bs.logout()
