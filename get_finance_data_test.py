from get_finance_data import *

def getStockDataFromCsvfile_test():
    pass

def getStockDataByCodeFromCsvfile_test():
    pass

def getStockType_test():
    pass

def getAllStockCode_test():
    pass

def getStockHistoryKData_test():
    pass

def getLastFetchTime_test():
    pass

def updateLastFetchTime_test():
    pass

def updateAllStockData_test():
    pass

def test():
    try:
        getStockDataFromCsvfile_test()
    except:
        print("getStockDataFromCsvfile failed")
    else:
        print("getStockDataFromCsvfile pass")
    #------------------------------
    try:
        getStockDataByCodeFromCsvfile_test()
    except:
        print("getStockDataByCodeFromCsvfile failed")
    else:
        print("getStockDataByCodeFromCsvfile pass")
    #------------------------------
    try:
        getStockType_test()
    except:
        print("getStockType failed")
    else:
        print("getStockType pass")
    #------------------------------
    try:
        getAllStockCode_test()
    except:
        print("getAllStockCode failed")
    else:
        print("getAllStockCode pass")
    #------------------------------
    try:
        getStockHistoryKData_test()
    except:
        print("getStockHistoryKData failed")
    else:
        print("getStockHistoryKData pass")
    #------------------------------
    try:
        getLastFetchTime_test()
    except:
        print("getLastFetchTime failed")
    else:
        print("getLastFetchTime pass")
    #------------------------------
    try:
        updateLastFetchTime_test()
    except:
        print("updateLastFetchTime failed")
    else:
        print("updateLastFetchTime pass")
    #------------------------------
    try:
        updateAllStockData_test()
    except:
        print("updateAllStockData failed")
    else:
        print("updateAllStockData pass")

if __name__ == "__main__":
    test()
