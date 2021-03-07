from baostock_structure import ALL_STOCK, STOCK_BASIC, MY_BASIC 
import baostock as bs
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import utils as u
import pickle

#TODO: change wb/rb
try:
    #f_allcodes = open('all_codes.pickle', 'wb')
    f_stocks = open('stock_data.pickle', 'rb')
    f_stocks_kline = open('stock_data_kline.pkl', 'wb')
    #f_indexes = open('index_data.pickle', 'wb')
    #f_others = open('other_data.pickle', 'wb')
except:
    print('fail to open files!')
lg = bs.login()
print('login respond error_code:'+lg.error_code)
print('login respond  error_msg:'+lg.error_msg)

'''
# fetch all codes
codes_dict = u.fetch_all_codes_and_tradestatus()
pickle.dump(codes_dict, f_allcodes)


# catregory all codes into three types
# mode = "stock": only handle stock type items
# mode = "index": only handle index type items
# mode = "other": only handle other type items
# mode = "all": handle all three types
####codes_dict = pickle.load(f_allcodes)
stocks_dict, indexes_dict, others_dict = u.fetch_ipodate_and_category_type(codes_dict, mode="all")
if bool(indexes_dict):
    pickle.dump(indexes_dict, f_indexes)
if bool(others_dict):
    pickle.dump(others_dict, f_others)
if bool(codes_dict):
    pickle.dump(stocks_dict, f_stocks)

'''

# fetch k line data for stocks
stocks_dict = pickle.load(f_stocks)
u.fetch_histkdata(stocks_dict=stocks_dict)
pickle.dump(stocks_dict, f_stocks_kline, protocol=pickle.HIGHEST_PROTOCOL)

#f_allcodes.close()
f_stocks.close()
f_stocks_kline.close()
#f_indexes.close()
#f_others.close()
bs.logout()
exit()


#### Get three types of stocks basic info ####
# define three types
# data=pickle.load(f)
stock_list = []
index_list = []
others_list = []

# get all stock code name
i=0
stocks_dict = {}
rs_all_stock = bs.query_all_stock()   #default use current day
while (rs_all_stock.error_code == '0') & rs_all_stock.next():
    i=i+1
    stock_dict = {}
    print('processing {}'.format(i) ,end = "")

    # get stock code, name, tradestatus 
    item_all_stock = rs_all_stock.get_row_data()  
    stock_dict[ALL_STOCK.code.name] = item_all_stock[ALL_STOCK.code]
    stock_dict[ALL_STOCK.code_name.name] = item_all_stock[ALL_STOCK.code_name]
    stock_dict[ALL_STOCK.tradeStatus.name] = item_all_stock[ALL_STOCK.tradeStatus]
    stock_code = item_all_stock[ALL_STOCK.code]
    
    # get basic info of this stock
    item_basic = bs.query_stock_basic(code=stock_code).get_row_data()
    if item_basic[STOCK_BASIC.status] == '1':  # is still in market, we ignore out of market stocks here
        if item_basic[STOCK_BASIC.type] == '1': # this is a stock
            stock_dict[STOCK_BASIC.ipoDate.name] = item_all_basic[STOCK_BASIC.ipoDate]
            # get history k data

        elif item_basic[STOCK_BASIC.type] == '2': # this is an index
            item_basic = item_basic[:3]
            item_basic.append(item_all_stock[ALL_STOCK.tradeStatus])
            index_list.append(item_basic)
        else:
            item_basic = item_basic[:3]
            item_basic.append(item_all_stock[ALL_STOCK.tradeStatus])
            others_list.append(item_basic)

stock_csv = pd.DataFrame(stock_list, columns=[MY_BASIC.code.name, MY_BASIC.code_name.name, MY_BASIC.ipoDate.name, MY_BASIC.tradeStatus.name])
stock_csv.to_csv("./all_stock.csv", encoding="utf-8", index=False)
stock_csv = pd.DataFrame(index_list, columns=[MY_BASIC.code.name, MY_BASIC.code_name.name, MY_BASIC.ipoDate.name, MY_BASIC.tradeStatus.name])
stock_csv.to_csv("./all_index.csv", encoding="utf-8", index=False)
stock_csv = pd.DataFrame(others_list, columns=[MY_BASIC.code.name, MY_BASIC.code_name.name, MY_BASIC.ipoDate.name, MY_BASIC.tradeStatus.name])
stock_csv.to_csv("./all_others.csv", encoding="utf-8", index=False)



#### log out ####
bs.logout()
