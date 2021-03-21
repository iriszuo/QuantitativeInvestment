import baostock as bs
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import pickle
from baostock_structure import STOCK_DICT
import sys
import os

#A_SHARE_START_DATE = "1984-11-18" # 1984年11月18日发行了第一支A股股票“飞乐音箱”
A_SHARE_START_DATE = "1990-12-19" # baostock库文档中给定最早可获取1990年12月19
                                 # 日的数据

def mkdir(path):
    '''
    make directory at path
    Args:
        path
    Returns:
        Bool:
            if path already exists, return False
            if make dictory Succeed, return True
    Raises:
        Exception("Make directory failed"): if os.makedirs failed
        
    '''
    folder = os.path.exists(path)
    if not folder:#判断是否存在文件夹如果不存在则创建为文件夹
        try:
            os.makedirs(path) #makedirs 创建文件时如果路径不存在会创建这个路径
        except:
            raise Exception("Make directory failed")
        return True
    else:
        return False


def get_stock_data_from_csvfile(file_path):
    """
    get stock data from csv file named file_path
    Args:
      file_path: the csv file that stored stock data wanted
    Returns:
      pandas DataFrame when success
      None when failed
    """
    try:
        data = pd.read_csv(file_path)
    except:
        return None
    return data


def get_stock_data_by_code_from_csvfile(code, path, stock_type = '1',prefix=""):
    """
    get stock data by code from csv file
    Args:
      code: the code of stock you want
      stock_type: stock type, '1' for share, '2' for index, '3' for other
      path: path to the diectory where store your stock data
      prefix: prefix of stock name
    Returns:
      pandas DataFrame when success
      None when failed
    """
    type_name = ""
    if(stock_type == '1'):
        type_name = "share/"
    elif(stock_type == '2'):
        type_name = "index/"
    else:
        type_name = "other/"
    file_path = path + type_name + prefix + code
    return get_stock_data_from_csvfile(file_path)

def save_all_stock_history_k_data(day=None, path = "", prefix = ""):
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
      Exception("Make directories path to share/index/other failed"): if make directories failed
      Exception("login failed"): if baostock login failed
      Exception("query all stock failed"): if get all stock basic info failed
    """
    path2share = path + "share/"
    path2index = path + "index/"
    path2other = path + "other/"

    try:
        mk_rs = mkdir(path2share) and mkdir(path2index) and mkdir(path2other)
    except Exception as err:
        print(err)
        raise Exception("Make directories path to share/index/other failed")

    result = 0
    lg = bs.login() # 登陆系统
    if(lg.error_code != '0'):
        raise Exception("login failed")

    if(day):
        rs = bs.query_all_stock(day=day) # 获取证券信息
    else:
        rs = bs.query_all_stock()
    if(rs.error_code != '0'):
        raise Exception("query all stock failed")
    while (rs.error_code == '0') & rs.next(): # 获取每个股票的历史k线数据
        code = rs.get_row_data()[0]
        rs_b = bs.query_stock_basic(code=code)
        if(rs_b.error_code != '0'): 
            print(code,'query_stock_basic respond error_code:'+rs_b.error_code)
            print(code,'query_stock_basic respond  error_msg:'+rs_b.error_msg)
            continue
        stock_basic_data = rs_b.get_row_data()
        if(len(stock_basic_data) < 6):
            print(code,'query_stock_basic: no basic data')
            continue

        rs_k = bs.query_history_k_data_plus(
                code,
                "date,\
                code,\
                open,\
                high,\
                low,\
                close,\
                preclose,\
                volume,\
                amount,\
                adjustflag,\
                turn,\
                tradestatus,\
                pctChg,\
                isST",
                start_date=A_SHARE_START_DATE,
                frequency="d",
                adjustflag="2")
        if(rs_k.error_code != '0'): 
            print('query_history_k_data respond error_code:'
                    + rs_k.error_code)
            print('query_history_k_data respond  error_msg:'
                    + rs_k.error_msg)
            continue
            # raise Exception("query history k data failed") # 不希望单个股票失败而停止整个程序
        data_k_list = []
        while (rs_k.error_code == '0') & rs_k.next():
            # 获取一条记录，将记录合并在一起
            tmp_data = rs_k.get_row_data()
            tmp_data.insert(2,stock_basic_data[1])
            tmp_data.insert(2,stock_basic_data[2])
            data_k_list.append(tmp_data)
        tmp_fields = rs_k.fields
        tmp_fields.insert(2,STOCK_DICT.code_name.name)
        tmp_fields.insert(2,STOCK_DICT.ipoDate.name)
        try:
            if(stock_basic_data[4] == '1'):
                pd.DataFrame(data_k_list, columns=tmp_fields)\
                        .to_csv(path2share + prefix + str(code),\
                        encoding="utf-8",index=False)
            if(stock_basic_data[4] == '2'):
                pd.DataFrame(data_k_list, columns=tmp_fields)\
                        .to_csv(path2index + prefix + str(code),\
                        encoding="utf-8",index=False)
            if(stock_basic_data[4] == '3'):
                pd.DataFrame(data_k_list, columns=tmp_fields)\
                        .to_csv(path2other + prefix + str(code),\
                        encoding="utf-8",index=False)
        except Exception as err:
            print("save share",code,"failed")
            print(err)
            continue
            #raise Exception("save share",code,"failed"") #不希望单个股票保存失败而停止整个程序
        result+=1
        if(result % 100 == 0):
            print("Saved",result,"shares")
    return result



if __name__ == "__main__":
    if(len(sys.argv) != 3):
        print("Usage: python get_finance_data.py \
path_to_save_data prefix_of_file")
        print("    path_to_save_data must end of '/',\
and no sub-dic named share, index, other in there")
    else:
        n = save_all_stock_history_k_data(\
                day = "2021-3-17",
                path = sys.argv[1],
                prefix = sys.argv[2]
                )
        print("Download data done")
        print("successfully saved",n, "shares")
