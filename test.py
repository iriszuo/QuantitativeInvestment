# coding=utf-8
import os
import sys
import numpy as np
import time
import baostock as bs
from datetime import datetime, timedelta
import pandas as pd
import utils as u
from tqdm import tqdm
from stockClass import Stock
import pickle
import traceback
from get_finance_data import get_stock_data_from_csvfile

#pd.set_option('display.max_rows',None)

start_date = "2019-01-01"
end_date = "2021-01-01"



if __name__ == '__main__':
    if (len(sys.argv) != 2):
        print("Usage: python test.py path_to_save_data")

    # set file path
    outFilename = "result/backtest.csv"
    errorFilename = "log/error_test_strategy.log"
    dataPath = sys.argv[1]

    # file for error log
    f=open(errorFilename, "a")
    
    # login baostock
    bs.login()

    # disable some warning for pandas
    pd.set_option('mode.chained_assignment', None)
 
    # if local has result csv file, check which stocks have been tested, skip them later
    exist_data_list = []
    if os.path.exists(outFilename):
        #index_col=0的作用是避免读取最左侧显示行数的数
        csv_data = pd.read_csv(outFilename, index_col=0, header=None)  
        exist_data_list = np.array(csv_data.iloc[2:,0])
    # if file not exist, create dataframe for the title
    else:
        df = pd.DataFrame(columns=('code','code_name', 'buy_cnt', 'buy_success','succ_ratio', 'max_gain', 'min_gain' ))
        df.to_csv(outFilename, mode='a',encoding='utf8')

    # fetch data from pickle
    '''
    start = time.time()
    f_stocks_kline = open('stock_data_kline.pkl', 'rb')
    stocks_dict = pickle.load(f_stocks_kline)
    f_stocks_kline.close()
    end = time.time()
    print("Finish data loading, {}s spent.".format(int(end-start)))
    '''

    # traverse each stock in the path
    stockFileList = os.listdir(dataPath)
    pbar = tqdm(stockFileList)
    i=0
    for csvName in pbar:

        # fetch data from csv
        csvPath = os.path.join(dataPath, csvName)
        stockData = get_stock_data_from_csvfile(csvPath)
        code = stockData.loc[1, 'code']
        
        pbar.set_description("Processing %s" % code)
        
        # if in exist list, skip
        if code in exist_data_list:
            print("already tested, skip.")
            continue

        df = pd.DataFrame(columns=('code','code_name', 'buy_cnt', 'buy_success','succ_ratio', 'max_gain', 'min_gain' ))
        
        # create stock class instance and get basic info
        stock = Stock(code, data=stockData)
        df.loc[0, 'code'] = code
        df.loc[0, 'code_name'] = stock.name

        # calculate begin date: ipo date + 400 days
        start_date = (datetime.strptime(stock.ipodate, "%Y-%m-%d") + timedelta(400)).strftime("%Y-%m-%d") 
        # skip those on market < 1.5 years
        if datetime.strptime(end_date, "%Y-%m-%d") - datetime.strptime(start_date, "%Y-%m-%d") < timedelta(180):
            continue
        
        # begin backtest, if encounter error, save error info and continue
        try:
            buy_cnt, buy_success, avg_max_gain, avg_min_gain = stock.backtest(stock.strategy_macd_kdj_cci, 31, start_date, end_date)
        except Exception as e:
            print (traceback.format_exc())
            f.write("stock {} has error! error msg:\n{}\n".format(code, str(traceback.format_exc())))
            continue

        # fetch output and save in dataframe
        df.loc[0, 'buy_cnt'] = buy_cnt
        df.loc[0, 'buy_success'] = buy_success
        if buy_cnt > 0:
            df.loc[0, 'succ_ratio'] = buy_success/buy_cnt
        else:
            df.loc[0, 'succ_ratio'] = 0
        df.loc[0, 'max_gain'] = avg_max_gain
        df.loc[0, 'min_gain'] = avg_min_gain
        print("Finish stock {}: buy_cnt={}, buy_success={}, succ_ratio={}, max_gain={}, min_gain{}".format(code, buy_cnt, buy_success, df.loc[0, 'succ_ratio'], avg_max_gain, avg_min_gain))
        i=i+1

        df.to_csv(outFilename,header=None,  mode='a',encoding='utf8')
    
    '''
    # calculate average results for all stocks
    df = pd.DataFrame(columns=('code','code_name', 'buy_cnt', 'buy_success','succ_ratio', 'max_gain', 'min_gain' ))
    df.loc[0, 'code'] = 'total'
    df.loc[0,'buy_cnt'] = df['buy_cnt'].sum()
    df.loc[0, 'buy_success'] = df['buy_success'].sum()
    if df.loc[0,'buy_cnt'] > 0: 
        df.loc[0, 'succ_ratio'] = df.loc[i, 'buy_success']/df.loc[i,'buy_cnt']
        df.loc[0, 'max_gain'] = df['max_gain'].mean()
        df.loc[0,'min_gain'] = df['min_gain'].mean()
    else:
        df.loc[0, 'succ_ratio'] = 0
        df.loc[i, 'max_gain'] = None
        df.loc[i,'min_gain'] = None

    df.to_csv("backtest.csv", encoding="utf-8", index=False)
    '''
    bs.logout()
