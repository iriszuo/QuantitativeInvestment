import baostock as bs
import pandas as pd
import utils as u
from tqdm import tqdm
from stockClass import Stock
import pickle
import time
#pd.set_option('display.max_rows',None)

start_date = "2019-01-01"
end_date = "2020-03-01"

if __name__ == '__main__':
    bs.login()

    # fetch data from pickle
    start = time.time()
    f_stocks_kline = open('stock_data_kline.pkl', 'rb')
    stocks_dict = pickle.load(f_stocks_kline)
    f_stocks_kline.close()
    end = time.time()
    print("Finish data loading, {}s spent.".format(int(end-start)))

    # create dataframe to save all backtest resuls
    df = pd.DataFrame(columns=('code','code_name'))

    # traverse each stock
    pbar = tqdm(stocks_dict.items())
    i=0
    for code,stockd in pbar:
        pbar.set_description("Processing %s" % code)

        # create stock class instance and get basic info
        stock = Stock(code, dict_self=stockd)
        df.loc[i, 'code'] = code
        df.loc[i, 'code_name'] = stock.name

        # begin backtest
        buy_cnt, buy_success, avg_max_gain, avg_min_gain = stock.backtest(stock.strategy_macd_kdj_cci, 15, stock.ipodate, end_date)
        df.loc[i, 'buy_cnt'] = buy_cnt
        df.loc[i, 'buy_success'] = buy_success
        if buy_cnt > 0:
            df.loc[i, 'succ_ratio'] = buy_success/buy_cnt
        else:
            df.loc[i, 'succ_ratio'] = 0
        df.loc[i, 'max_gain'] = avg_max_gain
        df.loc[i, 'min_gain'] = avg_min_gain
        print("Finish stock {}: buy_cnt={}, buy_success={}, succ_ratio={}, max_gain={}, min_gain{}".format(code, buy_cnt, buy_success, df.loc[i, 'succ_ratio'], avg_max_gain, avg_min_gain))
        i=i+1
    
    # calculate average results for all stocks
    df.loc[i, 'code'] = 'total'
    df.loc[i,'buy_cnt'] = df['buy_cnt'].sum()
    df.loc[i, 'buy_success'] = df['buy_success'].sum()
    if df.loc[i,'buy_cnt'] > 0: 
        df.loc[i, 'succ_ratio'] = df.loc[i, 'buy_success']/df.loc[i,'buy_cnt']
        df.loc[i, 'max_gain'] = df['max_gain'].mean()
        df.loc[i,'min_gain'] = df['min_gain'].mean()
    else:
        df.loc[i, 'succ_ratio'] = 0
        df.loc[i, 'max_gain'] = None
        df.loc[i,'min_gain'] = None

    df.to_csv("backtest.csv", encoding="utf-8", index=False)

    bs.logout()
