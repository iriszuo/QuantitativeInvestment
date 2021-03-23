from enum import IntEnum, unique


#A_SHARE_START_DATE = "1984-11-18" # 1984年11月18日发行了第一支A股股票“飞乐音箱”
A_SHARE_START_DATE = "1990-12-19" # baostock库文档中给定最早可获取1990年12月19
                                 # 日的数据

STOCK_ROOT_PATH = "./share_data/"
STOCK_SHARE_PATH = STOCK_ROOT_PATH + "share/"
STOCK_INDEX_PATH = STOCK_ROOT_PATH + "index/"
STOCK_OTHER_PATH = STOCK_ROOT_PATH + "other/"
STOCK_TYPE_SHARE = '1'
STOCK_TYPE_INDEX = '2'
STOCK_TYPE_OTHER = '3'


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

