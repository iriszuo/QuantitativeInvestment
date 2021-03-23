import os
import time

STOCK_TRADE_END_TIME_HOUR = 15
STOCK_TRADE_END_TIME_MIN = 30

def getTime():
    """
    Returns:
      time format as 2021-1-23
    Raises:
    """
    lt = time.localtime(time.time())
    return str(lt.tm_year) + "-" + str(lt.tm_mon) + "-" + str(lt.tm_mday)

def isTodayTradeEnd():
    """
    判断当天股市交易是否结束
    股市结束时间是STOCK_TRADE_END_TIME_HOUR时 STOCK_TRADE_END_MIN分
    Returns:
      True: 如果当天股市交易已经结束
      False: 如果当天股市交易还未结束
    """
    lt = time.localtime(time.time())
    if(lt.tm_hour > STOCK_TRADE_END_TIME_HOUR):
        if(lt.tm_min > STOCK_TRADE_END_TIME_MIN):
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
