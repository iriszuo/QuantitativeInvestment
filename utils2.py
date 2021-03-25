import os
import time
import baostock as bs
from datetime import datetime, timedelta
from settings import\
        STOCK_KDATA_UPDATE_TIME_DAY,\
        STOCK_KDATA_UPDATE_TIME_HOUR,\
        STOCK_KDATE_UPDATE_TIME_MIN,\
        STOCK_KDATA_MINUTE_UPDATE_TIME_DAY,\
        STOCK_KDATA_MINUTE_UPDATE_TIME_HOUR,\
        STOCK_KDATE_MINUTE_UPDATE_TIME_MIN,\
        STOCK_OTHER_FINANCE_DATA_UPDATE_TIME_DAY,\
        STOCK_OTHER_FINANCE_DATA_UPDATE_TIME_HOUR,\
        STOCK_OTHER_FINANCE_DATA_UPDATE_TIME_MIN



def getDate():
    """
    返回当前日期,格式为"2021-3-21"
    Returns:
      time format as 2021-1-23
    Raises:
    """
    lt = time.localtime(time.time())
    return str(lt.tm_year) + "-" + str(lt.tm_mon) + "-" + str(lt.tm_mday)


def isKdataUpdated(day = None):
    """
    判断baostock库上day(日期，格式为"2021-3-20")的k线数据（非分钟级）是否已经更新
    """
    if(not day):
        day = getDate()
    lt = time.localtime(time.time())
    year,month,day = a.split('-')
    if(lt.tm_year >= int(year)):
        if(lt.tm_mon >= int(month)):
            if(lt.tm_mday >= int(day) + STOCK_KDATA_UPDATE_TIME_DAY):
                if(lt.tm_hour >= STOCK_KDATA_UPDATE_TIME_HOUR):
                    if(lt.tm_min >= STOCK_KDATA_UPDATE_TIME_MIN):
                        return True
    return False

def isMinuteKdataUpdated(day = None):
    """
    判断baostock库上day(日期，格式为"2021-3-20")的分钟级k线数据是否已经更新
    """
    if(not day):
        day = getDate()
    lt = time.localtime(time.time())
    year,month,day = a.split('-')
    if(lt.tm_year >= int(year)):
        if(lt.tm_mon >= int(month)):
            if(lt.tm_mday >= int(day) + STOCK_KDATA_MINUTE_UPDATE_TIME_DAY):
                if(lt.tm_hour >= STOCK_KDATA_MINUTE_UPDATE_TIME_HOUR):
                    if(lt.tm_min >= STOCK_KDATA_MINUTE_UPDATE_TIME_MIN):
                        return True
    return False

def isOtherFinanceDataUpdated(day = None):
    """
    判断baostock库上day(日期，格式为"2021-3-20")的其他财经信息是否已经更新
    """
    if(not day):
        day = getDate()
    lt = time.localtime(time.time())
    year,month,day = a.split('-')
    if(lt.tm_year >= int(year)):
        if(lt.tm_mon >= int(month)):
            if(lt.tm_mday >= int(day) + STOCK_OTHER_FINANCE_DATA_UPDATE_TIME_DAY):
                if(lt.tm_hour >= STOCK_OTHER_FINANCE_DATA_UPDATE_TIME_HOUR):
                    if(lt.tm_min >= STOCK_OTHER_FINANCE_DATA_UPDATE_TIME_MIN):
                        return True
    return False


def isTradeDay(day):
    """
    判断day是否为交易日,day的格式为:"2021-3-23"
    是，返回1
    不是，返回0
    day的格式错误返回-1
    """
    lg = bs.login() # 登陆系统
    if(lg.error_code != '0'):
        raise Exception("login failed")
    trade_dates = bs.query_trade_dates(start_date=day, end_date=day).get_row_data()
    #bs.logout()
    if(len(trade_dates) == 0):
        return -1
    else:
        return int(trade_dates[1])

def getRecentTradeday(day=None):
    """
    获取day之前最接近day的交易日
    获取当前日期之前，最近的交易日期
    """
    if(not day):
        # 这种情况下，如果当天的交易还未结束，返回的交易日是不可用的
        day = getDate()
        if(not isKdataUpdated()):
            day = (datetime.strptime(day,"%Y-%m-%d") + timedelta(days=-1)).strftime("%Y-%m-%d")
    while True:
        if(isTradeDay(day)):
            return day
        else:
            day = (datetime.strptime(day,"%Y-%m-%d") + timedelta(days=-1)).strftime("%Y-%m-%d")


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
    '''
    folder = os.path.exists(path)
    if(os.path.exists(path)):
        return False
    else:#判断是否存在文件夹如果不存在则创建为文件夹
        try:
            os.makedirs(path) #makedirs 创建文件时如果路径不存在会创建这个路径
        except Exception as e:
            raise e
        return True
