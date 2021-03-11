import baostock as bs
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import pickle

#A_SHARE_START_DATE = "1984-11-18" # 1984年11月18日发行了第一支A股股票“飞乐音箱”
A_SHARE_START_DATE = "1990-12-19" # baostock库文档中给定最早可获取1990年12月19日的数据


def fetch_all_stock_history_k_data(day=None):
    """
    fetch history k-line data from IPO data of all stocks for specific trade date
    获取指定交易日所有股票自IPO日期以来的所有k线数据
    Args:
      day:
        specified trade day 指定交易日期
    Returns:
      list // or pandas DataFrame 列表或pandas的DataFramde
      {
          code: string
          tradeStatus: bool (1:normal, 0:suspended)
          code_name: string
          k-line-data: pandas DataFrame
      }
    Raises:
      ConnectionError: If connect to datasource failed
    """
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
        code = rs.get_row_data()[1]
        bs.query_history_k_data_plus(code, "date,code,open,high,low,close,preclose,volume,amount,adjustflag,turn,tradestatus,pctChg,isST", start_date=A_SHARE_START_DATE, frequency="d", adjustflag="2")

def save_all_stock_history_k_data(day=None, file_name="all_stock_history_k_data.csv"):
    """
    save history k-line data from IPO data of all stocks for specific trade date
    存储指定交易日所有股票自IPO日期以来的所有k线数据为csv文件
    Args:
      day:
        specified trade day 指定交易日期
    Returns:
      True: save succeed
      False: save data failed
    Raises:
      ConnectionError: If connect to datasource failed
    """
    #### 登陆系统 ####
    all_stock_history_k_data = fetch_all_stock_history_k_data(day=day)
    try:
        all_stock_history_k_data.to_csv(file_name)
    except:
        print("save data failed")
        raise IOError("save csv failed")
        return False
    return True

