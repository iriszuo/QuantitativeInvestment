# -*- coding:UTF-8 -*-
from enum import IntEnum, auto

# structures of different return value
class ALL_STOCK(IntEnum):
    code = 0
    tradeStatus = 1 # 正常交易1 or 停牌0
    code_name = 2

class STOCK_BASIC(IntEnum):
    code = 0
    code_name = 1
    ipoDate = auto()
    outDate = auto()
    type = auto()
    status = auto()

class MY_BASIC(IntEnum):
    code = 0
    code_name = 1
    ipoDate = auto()
    tradeStatus = auto()
    currentPrice = auto()
    oneYearPrice = auto()
    halfYearPrice = auto()
    oneYearRPS = auto()
    halfYearRPS = auto()

class STOCK_DICT(IntEnum):
    code = 0
    code_name = auto()
    ipoDate = auto()
    kdata = auto()

class HISTORY_K_DATA_PLUS(IntEnum):
    date = 0
    code = auto()
    open = auto()
    high = auto()
    low = auto()
    close = auto()
    preclose = auto()
    volume = auto()
    amount = auto()
    adjustflag = auto()
    turn = auto()
    tradestatus = auto()
    pctChg = auto()
    isST = auto()


