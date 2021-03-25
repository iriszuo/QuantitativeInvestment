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
