import baostock as bs
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import pickle

#A_SHARE_START_DATE = "1984-11-18" # 1984年11月18日发行了第一支A股股票“飞乐音箱”
A_SHARE_START_DATE = "1990-12-19" # baostock库文档中给定最早可获取1990年12月19日的数据


def save_all_stock_history_k_data(day=None, prefix = ""):
    """
    save history k-line data from IPO data of all stocks for specific trade date
    存储指定交易日所有股票自IPO日期以来的所有k线数据为csv文件
    Args:
      day:
        specified trade day 指定交易日期
        默认为当前交易日
      prefix:
        保存文件时，文件名的前缀。股票信息保存时被命名为prefix + code
    Returns:
      Integer: shares number that successfully saved
    Raises:
      ConnectionError: If connect to datasource failed
    """
    result = 0
    #### 登陆系统 ####
    lg = bs.login()
    # 显示登陆返回信息
    print('login respond error_code:'+lg.error_code)
    print('login respond  error_msg:'+lg.error_msg)

    #### 获取证券信息 ####
    if(day):
        rs = bs.query_all_stock(day=day)
    else:
        rs = bs.query_all_stock()
    print('query_all_stock respond error_code:'+rs.error_code)
    print('query_all_stock respond  error_msg:'+rs.error_msg)

    #### 获取每个股票的历史k线数据
    while (rs.error_code == '0') & rs.next():
        code = rs.get_row_data()[0]
        rs_k = bs.query_history_k_data_plus(code, "date,code,open,high,low,close,preclose,volume,amount,adjustflag,turn,tradestatus,pctChg,isST", start_date=A_SHARE_START_DATE, frequency="d", adjustflag="2")
        print('query_history_k_data_plus respond error_code:'+rs.error_code)
        print('query_history_k_data_plus respond  error_msg:'+rs.error_msg)
        data_k_list = []
        while (rs_k.error_code == '0') & rs_k.next():
            # 获取一条记录，将记录合并在一起
            data_k_list.append(rs_k.get_row_data())
        try:
            pd.DataFrame(data_k_list, columns=rs_k.fields).to_csv(prefix + str(code),encoding="utf-8",index=False)
        except:
            print("save share",code,"failed")
        result+=1
        if(result % 100 == 0):
            print("Saved",result,"shares")
    return result

if __name__ == "__main__":
    n = save_all_stock_history_k_data(prefix = "315-")
    print("Download data done")
    print("successfully saved",n, "shares")
