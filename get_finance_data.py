import baostock as bs
import pandas as pd
import sys
import time
import csv
import os
from utils2 import mkdir,\
        getRecentTradeday

from settings import STOCK_BASIC,\
        ALL_STOCK,\
        A_SHARE_START_DATE,\
        STOCK_DATA_ROOT_PATH,\
        STOCK_DATA_SHARE_PATH,\
        STOCK_DATA_INDEX_PATH,\
        STOCK_DATA_OTHER_PATH,\
        STOCK_TYPE_SHARE,\
        STOCK_TYPE_INDEX,\
        STOCK_TYPE_OTHER,\
        STOCK_DATA_UPDATETIME_LOG_FILE_NAME


def getStockDataFromCsvfile(file_path):
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


def getStockDataByCodeFromCsvfile(code, stock_type=None):
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
        #bs.logout()
        try:
            stock_type = stock_basic_data[STOCK_BASIC.type]
        except Exception as e:
            raise e
    file_path = ""
    if(stock_type == STOCK_TYPE_SHARE):
        file_path += STOCK_SHARE_PATH
    elif(stock_type == STOCK_TYPE_INDEX):
        file_path += STOCK_INDEX_PATH
    elif(stock_type == STOCK_TYPE_OTHER):
        file_path += STOCK_OTHER_PATH
    else:
        raise Exception("Unknown stock type")
    file_path += "/" + code + ".csv"
    return getStockDataFromCsvfile(file_path)

def getStockType(code):
    """
    获取code对应证券的类型
    '1'表示股票
    '2'表示指数
    '3'表示其他
    """
    lg = bs.login() # 登陆系统
    if(lg.error_code != '0'):
        raise Exception("login failed")
    rs_b = bs.query_stock_basic(code=code)
    if(rs_b.error_code != '0'): 
        print(code,'query_stock_basic respond error_code:'+rs_b.error_code)
        print(code,'query_stock_basic respond  error_msg:'+rs_b.error_msg)
    stock_basic_data = rs_b.get_row_data()
    #bs.logout()
    try:
        result = stock_basic_data[STOCK_BASIC.type]
    except Exception as e:
        raise e
    else:
        return result

def getAllStockCode(day = None):
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
        day = getRecentTradeday()
    rs = bs.query_all_stock(day=day) # 获取证券信息
    if(rs.error_code != '0'):
        raise Exception("query all stock failed")
    while (rs.error_code == '0') & rs.next(): # 获取每个股票的历史k线数据
        code = rs.get_row_data()[ALL_STOCK.code]
        result.append(code)
    #bs.logout()
    return result


def getAllShareCode(day = None):
    """
    获取交易日为day时，股市上所有股票的代码.
    Args:
      day: 交易日
          如果当日股票交易结束，默认为当日，否则为前一日
    Returns:
      list: 内容为表示股票代码的字符串
    """
    all_stock = getAllStockCode(day)
    all_share = []
    for stock in all_stock:
        if getStockType(stock) == '1':
            all_share.append(stock)
    return all_share



def getStockHistoryKData(code, startDay, endDay = None):
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
        endDay = getRecentTradeday()
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
    #bs.logout()
    return stock_basic_data[STOCK_BASIC.type], pd.DataFrame(data_k_list, columns=tmp_fields)


def getLastFetchTime(code):
    """
    获取股票代码为code的股票的上次更新时间
    Args:
    Returns:
      表示上次更新时间的字符串
      如果没有找到，返回None
    """
    if(not os.path.exists(STOCK_DATA_UPDATETIME_LOG_FILE_NAME)):
        return None
    with open(STOCK_DATA_UPDATETIME_LOG_FILE_NAME,'r') as f:
        for line in csv.DictReader(f):
            try:
                if(line['code'] == code):
                    return line['lastUpdateDate']
            except Exception as e:
                raise e
    return None


def updateLastFetchTime(code,updateTime):
    """
    更新股票代码为code的股票的上次获取时间，设置为updateTime
    Args:
    Returns:
      True
      False
    """
    # 在log文件中找到code对应的行（找不到说明还没有）
    # 是否要考虑找不到log文件的情况？
    if(not os.path.exists(STOCK_DATA_ROOT_PATH)):
        # 如果存储股票数据的根目录还没有，说明还没有数据，返回失败
        #os.makedirs(STOCK_DATA_ROOT_PATH)
        return False
    if(not os.path.exists(STOCK_DATA_UPDATETIME_LOG_FILE_NAME)):
        with open(STOCK_DATA_UPDATETIME_LOG_FILE_NAME,"w+") as f:
            writer = csv.writer(f)
            writer.writerow(['code','lastUpdateDate'])

    with open(STOCK_DATA_UPDATETIME_LOG_FILE_NAME) as inf,\
            open(STOCK_DATA_UPDATETIME_LOG_FILE_NAME + '.tmp', 'w') as outf:
                find = False
                reader = csv.reader(inf)
                writer = csv.writer(outf)
                for line in reader:
                    if(line[0] == code):
                        writer.writerow([line[0],updateTime])
                        find = True
                        break
                    else:
                        writer.writerow(line)
                if(not find):
                    # 没有找到对应code，新写入一行
                    writer.writerow([code,updateTime])
                writer.writerows(reader)
    os.remove(STOCK_DATA_UPDATETIME_LOG_FILE_NAME)
    os.rename(STOCK_DATA_UPDATETIME_LOG_FILE_NAME + '.tmp',\
            STOCK_DATA_UPDATETIME_LOG_FILE_NAME)


def updateAllStockData(day = None):
    """
    更新股票数据至交易日day，如果还没有下载过数据，会从零开始下载，并将数据按照正确类别分别存储在STOCK_DATA_SHARE_PATH、STOCK_DATA_INDEX_PATH、STOCK_DATA_OTHER_PATH中，同时记录更新每个code对应的更新时间，存储在STOCK_DATA_UPDATETIME_LOG_FILE_NAME中
    Args:
      day: 交易日
          如果当日股票交易结束，默认为当日
          否则向前找到最近的交易日
    Returns:
      int:成功更新数据的股票数
    Raises:
    """
    result = 0
    if(not day):
        day = getRecentTradeday()
    try:
        all_codes = getAllStockCode(day = day)
    except Exception as e:
        raise e
    else:
        to_csv_header = False
        path2root = STOCK_DATA_ROOT_PATH
        path2share = STOCK_DATA_SHARE_PATH
        path2index = STOCK_DATA_INDEX_PATH
        path2other = STOCK_DATA_OTHER_PATH
        try:
            mkdir(path2root) and mkdir(path2share) and mkdir(path2index) and mkdir(path2other)
        except Exception as err:
            raise err
        for code in all_codes:
            lastUpdateTime = getLastFetchTime(code)
            if(lastUpdateTime):
                # code 对应股票存在对应更新时间
                if(day == lastUpdateTime):
                    continue
            else:
                # code 对应股票不存在对应的最近更新时间，
                # 有理由相信该股票数据还未被下载
                # 从ipo之日开始下载该股票数据
                lastUpdateTime = A_SHARE_START_DATE
                # 创建csv文件时需要添加header
                to_csv_header = True
            # Q：要不要考虑更新时间大于当前时间的异常情况？
            try:
                stock_type, stock_kline_data = getStockHistoryKData(code, startDay = lastUpdateTime,endDay = day)
            except Exception as e:
                raise e
            stock_data_filename = ""
            if(stock_type == STOCK_TYPE_SHARE):
                stock_data_filename += path2share
            elif(stock_type == STOCK_TYPE_INDEX):
                stock_data_filename += path2index
            elif(stock_type == STOCK_TYPE_OTHER):
                stock_data_filename += path2other
            stock_data_filename +=  "/" + code + ".csv"
            stock_kline_data.to_csv(stock_data_filename,\
                    mode = 'a',\
                    encoding="utf-8",\
                    index=False,\
                    header= to_csv_header)
            # 更新last update time
            updateLastFetchTime(code,day)
            result+=1
            if(result % 100 == 0):
                print("Saved",result,"shares")
    return result
