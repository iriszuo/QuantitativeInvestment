#
# settings.py
#

from enum import IntEnum, unique
import sys


#A_SHARE_START_DATE = "1984-11-18" # 1984年11月18日发行了第一支A股股票“飞乐音箱”
A_SHARE_START_DATE = "1990-12-19" # baostock库文档中给定最早可获取1990年12月19
                                 # 日的数据

REPO_HOME_PATH = sys.path[0] # 获取当前运行脚本所在路径

LOG_PATH = REPO_HOME_PATH + "/log"
RESULT_PATH = REPO_HOME_PATH + "/result"
BACKTEST_RESULT_PATH = RESULT_PATH + "/backtest"

STOCK_DATA_ROOT_PATH = REPO_HOME_PATH + "/share_data" 
# 用于存储STOCK数据的根目录
STOCK_DATA_SHARE_PATH = STOCK_DATA_ROOT_PATH + "/share"
# 用于存储股票数据数据的目录
STOCK_DATA_INDEX_PATH = STOCK_DATA_ROOT_PATH + "/index"
# 用于存储指数数据数据的目录
STOCK_DATA_OTHER_PATH = STOCK_DATA_ROOT_PATH + "/other"
# 用于存储其他数据数据的目录
STOCK_TYPE_SHARE = '1'
STOCK_TYPE_INDEX = '2'
STOCK_TYPE_OTHER = '3'
# baostock库中STOCK类型的表示
STOCK_DATA_UPDATETIME_LOG_FILE_NAME = STOCK_DATA_ROOT_PATH + "/lastUpdateTime.csv"
# 用于存储所有Stock最近更新时间的文件名，格式为code,date

# baostock库每日最新数据更新时间：
STOCK_KDATA_UPDATE_TIME_DAY = 0
STOCK_KDATA_UPDATE_TIME_HOUR = 17
STOCK_KDATE_UPDATE_TIME_MIN = 30
# 当前交易日17:30，完成日K线数据入库；
STOCK_KDATA_MINUTE_UPDATE_TIME_DAY = 0
STOCK_KDATA_MINUTE_UPDATE_TIME_HOUR = 20
STOCK_KDATE_MINUTE_UPDATE_TIME_MIN = 30
# 当前交易日20:30，完成分钟K线数据入库；
STOCK_OTHER_FINANCE_DATA_UPDATE_TIME_DAY = 1
STOCK_OTHER_FINANCE_DATA_UPDATE_TIME_HOUR = 1
STOCK_OTHER_FINANCE_DATA_UPDATE_TIME_MIN = 30
# 第二自然日1:30，完成前交易日“其它财务报告数据”入库；



@unique
class ALL_STOCK(IntEnum):
    code = 0
    tradeStatus = 1
    code_name = 2


@unique
class STOCK_BASIC(IntEnum):
    code = 0
    code_name = 1
    ipoDate = 2
    outDate = 3
    type = 4
    status = 5

