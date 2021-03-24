import baostock as bs
import pandas as pd
import sys
import time
from utils2 import mkdir,\
        getTime,\
        isTodayTradeEnd

from settings import STOCK_BASIC,\
        ALL_STOCK,\
        A_SHARE_START_DATE,\
        STOCK_ROOT_PATH,\
        STOCK_SHARE_PATH,\
        STOCK_INDEX_PATH,\
        STOCK_OTHER_PATH,\
        STOCK_TYPE_SHARE,\
        STOCK_TYPE_INDEX,\
        STOCK_TYPE_OTHER,\
        STOCK_DATA_UPDATETIME_LOG_FILE_NAME


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


def get_stock_data_by_code_from_csvfile(code, stock_type=None):
    """
    get stock data by code from csv file
    Args:
      code: the code of stock you want
      stock_type: stock type, '1' for share, '2' for index, '3' for other
      path: path to the diectory where store your stock data
    Returns:
      pandas DataFrame when success
      None when failed
    """
    if(not stock_type):
        # get stock type by code
        lg = bs.login()
        if(lg.error_code != '0'):
            raise Exception("baostock login failed")
        rs_b = bs.query_stock_basic(code=code)
        if(rs_b.error_code != '0'): 
            raise Exception("baostock get stock basic information faild")
        stock_basic_data = rs_b.get_row_data()
        if(len(stock_basic_data) < 6):
            raise Exception("no basic information")
        stock_type = stock_basic_data[STOCK_BASIC.type]
    file_path = ""
    if(stock_type == STOCK_TYPE_SHARE):
        file_path += STOCK_SHARE_PATH
    elif(stock_type == STOCK_TYPE_INDEX):
        file_path += STOCK_INDEX_PATH
    elif(stock_type == STOCK_TYPE_OTHER):
        file_path += STOCK_OTHER_PATH
    else:
        raise Exception("Unknown stock type")
    file_path += code + ".csv"
    return get_stock_data_from_csvfile(file_path)

def get_all_stock_code(day = None):
    """
    获取交易日为day时，股市上所有股票的代码，包括股票、指数和其他
    Args:
      day: 交易日
          如果当日股票交易结束，默认为当日，否则为前一日
    Returns:
      list: 内容为表示股票代码的字符串
    Raises:
      Exception("login failed")
      Exception("query all stock failed")
    """
    result = []
    lg = bs.login() # 登陆系统
    if(lg.error_code != '0'):
        raise Exception("login failed")
    if(not day):
        lt = time.localtime(time.time())
        if(isTodayTradeEnd()):
            day = str(lt.tm_year) + "-" + str(lt.tm_mon) + "-" + str(lt.tm_mday)
        else:
            day = str(lt.tm_year) + "-" + str(lt.tm_mon) + "-" + str(lt.tm_mday - 1)
    rs = bs.query_all_stock(day=day) # 获取证券信息
    if(rs.error_code != '0'):
        raise Exception("query all stock failed")
    while (rs.error_code == '0') & rs.next(): # 获取每个股票的历史k线数据
        code = rs.get_row_data()[ALL_STOCK.code]
        result.append(code)
    return result

def get_stock_history_k_data(code, startDay, endDay = None):
    """
    获取股票代码为code的股票，从startDay到endDay的历史k线数据
    Args:
      code: 以字符串形式表示的股票代码
      startDay: 以字符串形式表示的日期，比如'2008-1-1'
      endDay: 以字符串形式表示的日期，比如'2008-1-1'。默认为当日交易日
    Returns:
      stock type, and a pandas DataFrame
      其中stock type是'1'、'2'、'3'字符表示的数字，表示股票的类型是股票、指数还是其他
      另外pandas DataFrame包含16列:
      date,code,ipoDate,code_name,open,high,low,close,preclose,volume,amount,adjustflag,turn,tradestatus,pctChg,isST
    Raises:
      raise Exception("login failed")
    """
    lg = bs.login() # 登陆系统
    if(lg.error_code != '0'):
        raise Exception("login failed")

    if(not endDay):
        lt = time.localtime(time.time())
        if(isTodayTradeEnd()):
            endDay = str(lt.tm_year) + "-" + str(lt.tm_mon) + "-" + str(lt.tm_mday)
        else:
            endDay = str(lt.tm_year) + "-" + str(lt.tm_mon) + "-" + str(lt.tm_mday - 1)
    rs_b = bs.query_stock_basic(code=code)
    if(rs_b.error_code != '0'): 
        print(code,'query_stock_basic respond error_code:'+rs_b.error_code)
        print(code,'query_stock_basic respond  error_msg:'+rs_b.error_msg)
    stock_basic_data = rs_b.get_row_data()
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
            start_date=startDay,
            frequency="d",
            adjustflag="2")
    if(rs_k.error_code != '0'): 
        print('query_history_k_data respond error_code:'
                + rs_k.error_code)
        print('query_history_k_data respond  error_msg:'
                + rs_k.error_msg)
    data_k_list = []
    while (rs_k.error_code == '0') & rs_k.next():
        # 获取一条记录，将记录合并在一起
        tmp_data = rs_k.get_row_data()
        tmp_data.insert(2,stock_basic_data[STOCK_BASIC.code_name])
        tmp_data.insert(2,stock_basic_data[STOCK_BASIC.ipoDate])
        data_k_list.append(tmp_data)
    tmp_fields = rs_k.fields
    tmp_fields.insert(2,STOCK_BASIC.code_name.name)
    tmp_fields.insert(2,STOCK_BASIC.ipoDate.name)
    return stock_basic_data[STOCK_BASIC.type], pd.DataFrame(data_k_list, columns=tmp_fields)



def save_all_stock_history_k_data(day=None):
    """
    save history k-line data from IPO data of all stocks for specific trade date, named by its code, end with .csv
      TODO: 在写k线数据的同时，更新该code的最近更新时间

    存储指定交易日所有股票自IPO日期以来的所有k线数据为csv文件,以其股票代码为名
    Args:
      day:
        specified trade day 指定交易日期
        今日交易日结束半小时以上，默认为当前交易日，否则默认为上个交易日
    Returns:
      Integer: shares number that successfully saved
    Raises:
      Exception("Make directories path to share/index/other failed"): if make directories failed
      Exception("login failed"): if baostock login failed
      Exception("query all stock failed"): if get all stock basic info failed
    """
    path2root = STOCK_ROOT_PATH
    path2share = STOCK_SHARE_PATH
    path2index = STOCK_INDEX_PATH
    path2other = STOCK_OTHER_PATH

    try:
        mk_rs = mkdir(path2root) and mkdir(path2share) and mkdir(path2index) and mkdir(path2other)
    except Exception as err:
        print(err)
        raise Exception("Make directories path to share/index/other failed")

    result = 0
    lg = bs.login() # 登陆系统
    if(lg.error_code != '0'):
        raise Exception("login failed")

    all_code = get_all_stock_code(day = day)
    for code in all_code:
        stock_type, k_data = get_stock_history_k_data(code, startDay = A_SHARE_START_DATE, endDay = day)
        try:
            if(stock_type == STOCK_TYPE_SHARE):
                k_data.to_csv(path2share + str(code) + ".csv",\
                        encoding="utf-8",index=False)
            elif(stock_type == STOCK_TYPE_INDEX):
                k_data.to_csv(path2index + str(code) + ".csv",\
                        encoding="utf-8",index=False)
            elif(stock_type == STOCK_TYPE_OTHER):
                k_data.to_csv(path2other + str(code) + ".csv",\
                        encoding="utf-8",index=False)
        except Exception as err:
            print("save share",code,"failed")
            print(err)
            continue
        result+=1
        if(result % 100 == 0):
            print("Saved",result,"shares")
    return result


def getLastFetchTime():
    """
    获取股票数据上次更新的时间
    Returns:
      Str: 上次更新时间的字符串
    Raises:
      FileNotFoundError: 如果文件不存在
      PermissionError: 如果没有权限读取文件
    """
    with open(STOCK_DATA_UPDATETIME_LOG_FILE_NAME,'r') as f:
        return f.readline()


def updateLastFetchTime():
    """
    logFile record last time when update share's data
    Raises:
    """
    updateTime = getTime();
    with open(STOCK_DATA_UPDATETIME_LOG_FILE_NAME,'w') as f:
        f.write(updateTime)

def update_all_stock_data(day = None):
    """
    更新股票数据至交易日day
    Args:
      day: 交易日
          如果当日股票交易结束，默认为当日，否则为前一日
    Returns:
    Raises:
    """
    if(not day):
        lt = time.localtime(time.time())
        if(isTodayTradeEnd()):
            day = str(lt.tm_year) + "-" + str(lt.tm_mon) + "-" + str(lt.tm_mday)
        else:
            day = str(lt.tm_year) + "-" + str(lt.tm_mon) + "-" + str(lt.tm_mday - 1)
    lastUpdateTime = getLastFetchTime()
    if(day == lastUpdateTime):
        return
    else:
        # 获取所有code
        # 判断code对应数据是否已经有文件
        # 如果已经有文件，读取文件数据上次更新时间
        # **数据更新时间开始的时候设想所有code共用一个时间，但是现在看来需要每个code 对应一个**
        # 如果还没有文件，从该股票ipo日期开始下载文件
        pass

    # to_csv("file.csv",mode='a', header = False)

if __name__ == "__main__":
    n = save_all_stock_history_k_data()
    print("Download data done")
    print("successfully saved",n, "shares")
