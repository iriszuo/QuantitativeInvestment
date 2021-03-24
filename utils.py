from baostock_structure import MY_BASIC, HISTORY_K_DATA_PLUS, ALL_STOCK, STOCK_BASIC
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import baostock as bs
from tqdm import tqdm

'''按照行数和列名的方式获取dataframe中的某个单元格值
input:
    row_index: 行数，为int类型
    col_name: 列名，为字符串类型
output：
    单元格值
'''
def get_df_value(df, row_index, col_name):
    return df.iloc[row_index, df.columns.get_loc(col_name)]

'''将两个dataframe按行合并起来
input:
    dfl:左边的dataframe
    dfr:右边的dataframe
    index:按照某列的标题将上面两个df合并起来。
output:
    合并后的dataframe。比如，dfl和dfr都有'date'这一列，其他列不一样，那么将index设置为'date',就会将'date'列保留，其他列左右合并起来。
'''
def join_df_column(dfl, dfr, index):
    return dfl.join(dfr.set_index(index), on=index)

    
'''获取上市超过一定时间的股票列表
input:
    stock_list:需要过滤的股票列表。
    days:上市超过days天的股票才会被留下。
    base:基准时间。"%Y-%m-%d"格式。如2015-01-01。则本函数会过滤出在2015年1月1号这个时间点，上市超过days天的股票的列表。
output:
    过滤后的股票列表，list形式，每个元素为字符串形式的股票代码。
'''
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


'''判断给定日期是否是交易日
input:
    date:给定日期
output:
    交易日返回true，非交易日，如节假日或者周末，返回false
'''
def is_tradeday(date):
    item_if_tradeday = bs.query_trade_dates(start_date=date, end_date=date).get_row_data()
    if_tradeday = int(item_if_tradeday[1])
    return if_tradeday


'''获取离给定日期最近的交易日（向前数），格式为字符串
'''
def get_recent_tradeday(date):
    while True:
        if_tradeday = is_tradeday(date)
        if if_tradeday:
            return date
        else:
            date = (datetime.strptime(date,"%Y-%m-%d") + timedelta(days=-1)).strftime("%Y-%m-%d")

'''获取给定时间段的k线数据
暂时用不到，因为类中有这个功能。
如果以后需要在类外用，需要迁移到get_finance_data.py中
'''
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



