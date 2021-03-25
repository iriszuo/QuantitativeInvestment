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

    ''' test stockClass.py __init__
    description:
        fetch data from csv file and create stock instance
    sub-test:
        get_finance_data: get_stock_data_from_csvfile
    '''
    df = get_stock_data_from_csvfile(csvPath)
    stock = Stock(code, data=df)
    print("Test stockClass.py __init__ done!")


    ''' test stockClass.py backtest
    sub-test:
        stockClass: strategy_macd_kdj_cci
        stockClass: basic_period_stock_gains
        stockClass: basic_period_hisdata
        stockClass: bench_MACD
        stockClass: bench_KDJ
        stockClass: bench_CCI
        utils: join_df_column
        utils: get_df_value
    '''
    buycnt, buysucc, avgmax, avgmin = stock.backtest(stock.strategy_macd_kdj_cci, 15, startdate, enddate)
    print("Test stockClass.py backtest done! --- ", buycnt, buysucc, avgmax, avgmin)
    

    '''test RPS
    sub-test:
        help_cal_bench: gain_dict_for_rps
    '''
    # TODO: use new API once it is ready
    dict_rps = gain_dict_for_rps(stock_list, enddate, 120)
    rps = stock.bench_RPS(dict_rps)
    print("Test stockClass.py bench_RPS done! --- ", rps)
    

    ''' test RSI
    '''
    hisdata = stock.basic_period_hisdata(startdate, enddate)
    df = stock.bench_RSI(hisdata)
    print("Test stockClass.py bench_RSI test done! --- ", df)

    bs.logout()
