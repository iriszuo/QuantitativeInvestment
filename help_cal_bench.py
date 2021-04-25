import numpy as np
import pandas as pd
import baostock as bs
from datetime import datetime, timedelta
import utils as u
from baostock_structure import MY_BASIC
import talib as ta
from stockClass import Stock
from get_finance_data import getStockDataByCodeFromCsvfile, getStockPeriodGain

'''计算所有股票在一段时间内的涨跌幅并按从大到小排序,为计算RPS做准备。
input:
    stock_list: 所有股票代码的list
    base_date:时间段的终点
    diff_days:往前数多少天。base_date - diff_days为时间段的起点。
output:
    sorted_dict: 排序好的字典（从大到小），key为股票代码，value为它在给定时间内的涨跌幅。 
exception:
    若给定时间内无交易日，返回空字典。
'''
def gain_dict_for_rps(stock_list, base_date, diff_days):
    begin_date = (datetime.strptime(base_date,"%Y-%m-%d") - timedelta(days=diff_days)).strftime("%Y-%m-%d")
    end_date = base_date
    gain_dict = {}
    for stock_code in stock_list:
        gain = getStockPeriodGain(stock_code, begin_date, end_date)
        if gain == False:
            # for this stock, no tradeday during given period, gain=0
            gain_dict[stock_code] = 0
        gain_dict[stock_code] = gain
    sorted_dict = sorted(gain_dict.items(), key=lambda x: x[1], reverse=True)
    return sorted_dict


####################################################
# calculate multiple stocks rsi for a specific period
# 50-80 buy, 0-20 may over sold
# long time period will lead to more accurate res
####################################################
def RSI(code_list, startdate, enddate):
    rsi_list = []
    for stock in code_list:
        # fetch close price data
        hisdata = u.get_his_k_data(stock, startdate, enddate)
        closelist = hisdata['close'] 
        
        # calculate rsi
        rsi_12days = ta.RSI(closelist,timeperiod=12) 
        rsi_6days = ta.RSI(closelist,timeperiod=6)
        rsi_24days = ta.RSI(closelist,timeperiod=24)
        hisdata['rsi_6days'] = rsi_6days 
        hisdata['rsi_12days'] = rsi_12days 
        hisdata['rsi_24days'] = rsi_24days
        rsi_buy_position = hisdata['rsi_6days'] > 80
        rsi_sell_position = hisdata['rsi_6days'] < 20 
        
        # judge overbought and oversold
        # current day is in buy status but next day is not, means current day is overbought
        hisdata.loc[rsi_buy_position[(rsi_buy_position == True) & (rsi_buy_position.shift() == False)].index, 'overbought'] = True 
        hisdata.loc[rsi_sell_position[(rsi_sell_position == True) & (rsi_sell_position.shift() == False)].index, 'oversold'] = True

        # generate final output
        df2 = hisdata[['date','rsi_6days','rsi_12days','rsi_24days','overbought','oversold']]
        rsi_list.append(df2)

    return rsi_list


