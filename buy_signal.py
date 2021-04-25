# coding=utf-8
import baostock as bs
import os
from datetime import datetime, timedelta
import pandas as pd
from tqdm import tqdm
from stockClass import Stock
from settings import LOG_PATH, RESULT_PATH, STOCK_DATA_SHARE_PATH
from get_finance_data import updateAllStockData, getAllShareCode, getStockDataFromCsvfile, getLastFetchTime, getStockDataByCodeFromCsvfile
from help_cal_bench import gain_dict_for_rps
from utils import getRecentTradeday
import traceback

if __name__ == '__main__':
    # disable some warning for pandas
    pd.set_option('mode.chained_assignment', None)

    # today time
    today = datetime.today()
    date = today.strftime("%Y-%m-%d")

    # get recent trade day
    date = getRecentTradeday(date) 

    # output file names
    script_name = os.path.basename(__file__).split('.')[0]
    outFileName = RESULT_PATH + "/" + script_name + "_" + date + "_result.csv"
    errorFileName = LOG_PATH + "/" + script_name + "_" + date + "_error.log"

    # open files
    if not os.path.exists(RESULT_PATH):
        mkdir(RESULT_PATH)
    if not os.path.exists(LOG_PATH):
        mkdir(LOG_PATH)
    f_error=open(errorFileName, "a")

    # login baostock
    lg = bs.login()
    if(lg.error_code != '0'):
        raise Exception("baostock login failed")

    # update kline data
    update_num = updateAllStockData(date)
    print("{} stock's k data updated!".format(update_num))

    # if local has result csv file, check which stocks have been tested, skip them later
    exist_data_list = []
    if os.path.exists(outFileName):
        try:
            #index_col=0的作用是避免读取最左侧显示行数的数
            csv_data = pd.read_csv(outFileName, index_col=0, header=None)  
            exist_data_list = np.array(csv_data.iloc[2:,0])
        except Exception as e:
            print("read empty outfile!")
            
    else:
        # if file not exist, create dataframe for the title
        df = pd.DataFrame(columns=('code', 'code_name', 'signal', 'rps'))
        df.to_csv(outFileName, mode='a',encoding='utf8')

    # calculate sorted dict for rps
    all_share_list = getAllShareCode(date) 
    sorted_dict_rps = gain_dict_for_rps(all_share_list, date, 180)

    # traverse each stock in the path
    shareFileList = os.listdir(STOCK_DATA_SHARE_PATH)
    pbar = tqdm(shareFileList)
    i=0
    for csvName in pbar:
        # fetch data from csv
        csvPath = os.path.join(STOCK_DATA_SHARE_PATH, csvName)
        shareDfData = getStockDataFromCsvfile(csvPath)
        code = shareDfData.loc[1, 'code']
        
        pbar.set_description("Processing %s" % code)
        
        # if in exist list, skip
        if code in exist_data_list:
            print("{} already tested, skip.".format(code))
            continue

        # if this stock has not been updated, skip
        if getLastFetchTime(code) != date:
            print("{} data not updated, skip.".format(code))
            f_error.write("stock {} data not updated, skip.\n\n".format(code))
            continue
        
        # create stock class instance and get basic info
        stock = Stock(code, data=shareDfData)
        try:
            succ = stock.strategy_macd_kdj_cci(date) 
        except Exception as e:
            print (traceback.format_exc())
            f_error.write("stock {} has error! error msg:\n{}\n\n".format(code, str(traceback.format_exc())))
            continue

        if succ:
            df = pd.DataFrame(columns=('code','code_name', 'signal', 'rps'))
            df.loc[0, 'code'] = stock.code
            df.loc[0, 'code_name'] = stock.name
            df.loc[0, 'signal'] = 'buy'

            # calculate rps for reference
            rps = stock.bench_RPS(sorted_dict_rps)
            df.loc[0, 'rps'] = rps

            df.to_csv(outFileName, header=None,  mode='a',encoding='utf8')
    print("finish processing!")
