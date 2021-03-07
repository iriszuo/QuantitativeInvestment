from baostock_structure import MY_BASIC, HISTORY_K_DATA_PLUS, ALL_STOCK, STOCK_BASIC
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import baostock as bs
from strategy import strategy
from tqdm import tqdm

def fetch_all_codes_and_tradestatus(date=""):
    codes_dict = {}

    rs_all_stock = bs.query_all_stock(day=date)   #default use current day
    while (rs_all_stock.error_code == '0') & rs_all_stock.next():
        code_dict = {}
        # get stock code, name, tradestatus 
        item_all_stock = rs_all_stock.get_row_data()  
        code_dict[ALL_STOCK.code.name] = item_all_stock[ALL_STOCK.code]
        code_dict[ALL_STOCK.code_name.name] = item_all_stock[ALL_STOCK.code_name]
        
        codes_dict[item_all_stock[ALL_STOCK.code]] = code_dict
    return codes_dict
 
def fetch_ipodate_and_category_type(codes_dict, mode="all"):
    pbar = tqdm(codes_dict.items())
    stocks_dict={}
    indexes_dict={}
    others_dict={}

    for code, value in pbar:
        pbar.set_description("Processing fetch ipodate and category type: %s" % code)
        item_basic = bs.query_stock_basic(code=code).get_row_data()
        if item_basic[STOCK_BASIC.status] == '1':  # is still in market, we ignore out of market stocks here
            if item_basic[STOCK_BASIC.type] == '1' and (mode=="all" or mode =="stock"): # this is a stock
                stocks_dict[code] = value
                stocks_dict[code][STOCK_BASIC.ipoDate.name] = item_basic[STOCK_BASIC.ipoDate]
            elif item_basic[STOCK_BASIC.type] == '2' and (mode=="all" or mode=="index"): # this is an index
                indexes_dict[code] = value
                indexes_dict[code][STOCK_BASIC.ipoDate.name] = item_basic[STOCK_BASIC.ipoDate]
            elif item_basic[STOCK_BASIC.type] == '3' and (mode=="all" or mode=="other"): # this is other type
                others_dict[code] = value
                ohters_dict[code][STOCK_BASIC.ipoDate.name] = item_basic[STOCK_BASIC.ipoDate]
   
    return stocks_dict, indexes_dict, others_dict

def fetch_histkdata(stocks_dict=None, code=None):
    # support two modes of input
    if bool(code):
        in_dict = {}
        in_dict[code] = None
    else:
        in_dict = stocks_dict

    pbar = tqdm(in_dict.items())
    for code,value in pbar:
        pbar.set_description("Processing fetch history k data: %s" % code)
        # calculate from ipo to today
        startdate=value[STOCK_BASIC.ipoDate.name]
        enddate=""  # empty means recent trade day
        rs = bs.query_history_k_data_plus(code, "date,code,open,high,low,close,preclose,volume,amount,adjustflag,turn,tradestatus,pctChg,isST", start_date=startdate, end_date=enddate, frequency="d", adjustflag="2")
        data_list = []
        while (rs.error_code == '0') & rs.next():
            data_list.append(rs.get_row_data())
        df_init = pd.DataFrame(data_list, columns=rs.fields) 
        df_status = df_init[df_init['tradestatus'] == '1'] # remove suspension days
        df_status = df_status.reset_index(drop=True)
        df_status.loc[:,'open'] = df_status.loc[:,'open'].astype(float) 
        df_status.loc[:,'high'] = df_status.loc[:,'high'].astype(float) 
        df_status.loc[:,'low'] = df_status.loc[:,'low'].astype(float) 
        df_status.loc[:,'close'] = df_status.loc[:,'close'].astype(float)

        value['kdata'] = df_status

   


def load_stock_from_csv():
    stocks = pd.read_csv('all_stock.csv')
    stock_code = stocks['code']
    stock_code = stock_code.tolist()
    return stock_code, stocks

def load_stock_IPO_above(stock_list, days, base):
    stock_filtered = []
    for item in stock_list:
        stock_code = item[MY_BASIC.code]
        date1=datetime.strptime(base,"%Y-%m-%d")
        date2=datetime.strptime(item[MY_BASIC.ipoDate],"%Y-%m-%d")
        num=(date1-date2).days
        if num >= days:
            stock_filtered.append(item)
    return stock_filtered 

def get_stock_price(stock_code, date):
    df = get_his_k_data(stock_code, date, date)
    if df.shape[0] == 0:
        return False  # 停牌
    price = df.loc[0,'close']
    return price 

def is_tradeday(date):
    item_if_tradeday = bs.query_trade_dates(start_date=date, end_date=date).get_row_data()
    if_tradeday = int(item_if_tradeday[1])
    return if_tradeday

def get_recent_tradeday(date):
    while True:
        if_tradeday = is_tradeday(date)
        if if_tradeday:
            return date
        else:
            date = (datetime.strptime(date,"%Y-%m-%d") + timedelta(days=-1)).strftime("%Y-%m-%d")


def get_his_k_data(code, startdate, enddate):
    rs = bs.query_history_k_data(code, "date,code,open,high,low,close,tradeStatus,preclose,volume,amount,pctChg", start_date=startdate, end_date=enddate, frequency="d", adjustflag="2")
    data_list = []
    while (rs.error_code == '0') & rs.next():
        data_list.append(rs.get_row_data())
    df_init = pd.DataFrame(data_list, columns=rs.fields) 
    df_status = df_init[df_init['tradeStatus'] == '1'] # remove stop trading stocks
    df_status = df_status.reset_index(drop=True)
    df_status.loc[:,'open'] = df_status.loc[:,'open'].astype(float) 
    df_status.loc[:,'high'] = df_status.loc[:,'high'].astype(float) 
    df_status.loc[:,'low'] = df_status.loc[:,'low'].astype(float) 
    df_status.loc[:,'close'] = df_status.loc[:,'close'].astype(float)
    return df_status

# judge k line is positive or negtive
def judge_kline_function(open_p, close_p):
    if open_p > close_p: 
        return 'negative'
    else:
        return 'positive'

def judge_kline_category(code, startdate, enddate):
    df_status = get_his_k_data(code, startdate, enddate) 
    df_status['kline_category'] = df_status.apply(lambda x: judge_kline_function(x.open, x.close), axis=1)
    return df_status

def k_line_ma(code, startdate, enddate, days):
    hisdata = get_his_k_data(code, startdate, enddate)
    hisdata['MA_' + str(days)] = pd.rolling_mean(hisdata['close'], days)
    df2 = hisdata[['date','MA_'+str(days)]] 
    return df2

def period_stock_gains(stock_code, begin_date, end_date):
    assert datetime.strptime(begin_date, "%Y-%m-%d") <= datetime.strptime(end_date, "%Y-%m-%d")
    old_date = get_recent_tradeday(begin_date)
    current_date = get_recent_tradeday(end_date)
    # if contain suspension days, return False
    old_price = float(get_stock_price(stock_code, old_date))
    if old_price==False:
        return False

    current_price = float(get_stock_price(stock_code, current_date))
    if current_price==False:
        return False

    gains = (current_price - old_price) / old_price
    return gains


def backtest_core(code, startdate, enddate, holddays):
    startdate_t = datetime.strptime(startdate, "%Y-%m-%d")
    enddate_t = datetime.strptime(enddate, "%Y-%m-%d")
    buy_cnt = 0
    buy_success = 0
    max_gain_list=[]
    min_gain_list=[]
    avg_max_gain = None
    avg_min_gain = None

    for date in range((enddate_t - startdate_t).days + 1):
        date = startdate_t + timedelta(date)
        date = date.strftime("%Y-%m-%d")
        if not is_tradeday(date):
            continue
        is_buy = strategy(code, date)
        if is_buy:
            buy_cnt = buy_cnt + 1
            gain_list = []
            begin_date = date
            for days in range(1, holddays+1):
                end_date = (datetime.strptime(date, "%Y-%m-%d") + timedelta(days=days)).strftime("%Y-%m-%d")
                # skip non-tradeday
                if not is_tradeday(end_date):
                    continue
                gain = period_stock_gains(code, begin_date, end_date)
                # skip suspension
                if gain==False:
                    continue
                gain_list.append(gain)
            max_gain = np.max(gain_list)
            max_gain_list.append(max_gain)
            min_gain = np.min(gain_list)
            min_gain_list.append(min_gain)
            if max_gain >= 0.1:
                buy_success = buy_success + 1
    if max_gain_list:
        avg_max_gain = np.average(max_gain_list)
    if min_gain_list:
        avg_min_gain = np.average(min_gain_list)
    return buy_cnt, buy_success, avg_max_gain, avg_min_gain                

def join_df_column(dfl, dfr, index):
    return dfl.join(dfr.set_index(index), on=index)
