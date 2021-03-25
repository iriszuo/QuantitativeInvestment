# coding=utf-8
import baostock as bs
from datetime import datetime, timedelta
import pandas as pd
from tqdm import tqdm
from stockClass import Stock



if __name__ == '__main__':
    # file names
    outFileName = "buy.csv"
    errorFileName = "error_buy.log"

    # open files
    f_error=open(errorFileName, "a")
    f_res = open(outFileName, "w")

    # login baostock
    bs.login()

    # today time
    today = datetime.datetime.today()
    date = today.strftime("%Y-%m-%d")

    # traverse folders, append today's k line data to file, calculate buy signal and write to file
    df = pd.DataFrame(columns=('code', 'code_name'))
    stock = Stock(code, df??)
    try:
        succ = stock.strategy_macd_kdj_cci(date) 
    except Exception as e:
            print (traceback.format_exc())
            f.write("stock {} has error! error msg:\n{}\n".format(code, str(traceback.format_exc())))
            continue

    if succ:
        df.loc[0, 'code'] = stock.code
        df.loc[0, 'code_name'] = stock.name
        df.to_csv(outFileName, header=None,  mode='a',encoding='utf8')
