from utils2 import *
import re


def getDate_test():
    date = getDate()
    assert(type(date) == str)
    date_re_pattern = '((((19|20)\d{2})-(0?(1|[3-9])|1[012])-(0?[1-9]|[12]\d|30))|(((19|20)\d{2})-(0?[13578]|1[02])-31)|(((19|20)\d{2})-0?2-(0?[1-9]|1\d|2[0-8]))|((((19|20)([13579][26]|[2468][048]|0[48]))|(2000))-0?2-29))$'
    assert(re.search(date_re_pattern,date))

def isKdataUpdated_test():
    pass

def isMinuteKdataUpdated_test():
    pass

def isOtherFinanceDataUpdated_test():
    pass

def isTradeDay_test():
    pass

def getRecentTradeday_test():
    pass

def mkdir_test():
    pass

def test():
    try:
        getDate_test()
    except:
        print("getDate failed")
    else:
        print("getDate pass")
    #---------------------
    try:
        isKdataUpdated_test()
    except:
        print("isKdataUpdated failed")
    else:
        print("isKdataUpdated pass")
    #---------------------
    try:
        isMinuteKdataUpdated_test()
    except:
        print("isMinuteKdataUpdated failed")
    else:
        print("isMinuteKdataUpdated pass")
    #---------------------
    try:
        isOtherFinanceDataUpdated_test()
    except:
        print("isOtherFinanceDataUpdated failed")
    else:
        print("isOtherFinanceDataUpdated pass")
    #---------------------
    try:
        isTradeDay_test()
    except:
        print("isTradeDay failed")
    else:
        print("isTradeDay pass")
    #---------------------
    try:
        getRecentTradeday_test()
    except:
        print("getRecentTradeday failed")
    else:
        print("getRecentTradeday pass")
    #---------------------
    try:
        mkdir_test()
    except:
        print("mkdir failed")
    else:
        print("mkdir pass")


if __name__ == "__main__":
    test()


