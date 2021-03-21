import numpy as np
import pandas as pd
import baostock as bs
from datetime import datetime, timedelta
import utils as u
from baostock_structure import MY_BASIC
import talib as ta

####### for RPS ##########
######
##########################

# calculate all stocks' period gain and sort, this is for rps calculation
'''计算所有股票在一段时间内的涨跌幅并按从大到小排序,为计算RPS做准备。
input:
    stock_list: 所有股票代码的list
    base_date:时间段的终点
    diff_days:往前数多少天。base_date - diff_days为时间段的起点。
output:
    sorted_dict: 排列好的字典，key为股票代码，value为它在给定时间内的涨跌幅。 
'''
def rps(stock_list, base_date, diff_days):
    gain_dict = {}
    i=0
    for stock in stock_list:
        i=i+1
        gain_dict[stock[MY_BASIC.code]] = u.period_stock_gains(stock[MY_BASIC.code], base_date, diff_days)
    sorted_dict = sorted(gain_dict.items(), key=lambda x: x[1], reverse=True)
    total_num = len(gain_dict)
    # list format: stock code, rps, gains
    rps_list = []
    for i, stock in enumerate(sorted_dict):
        code = stock[0]
        gain = stock[1]
        rps = (1 - (i+1) / total_num) * 100
        print('rps cal {}:{},{},{}'.format(i, code, gain, rps))
        rps_list.append([code, rps, gain*100])
    stock_csv = pd.DataFrame(rps_list, columns=[MY_BASIC.code.name, 'rps', 'gains']) 
    stock_csv.to_csv("./rps_0205_120.csv", encoding="utf-8", index=False)
    return rps_list

####################################################
# calculate multiple stocks cci for a specific period
# cci > 100/ cci < -100 but change direction: buy
# cci < -100/ cci > 100 but change direction: sell
####################################################
def CCI(hisdata, df):
    df_out = df.copy()
    highlist = hisdata['high'] 
    lowlist = hisdata['low']
    closelist = hisdata['close'] 
    CCIlist = ta.CCI(highlist,lowlist,closelist) # default timeperiod=14, means use 14 days mean average
    CCIlist = list(CCIlist)
    df_out['CCI_14'] = CCIlist
    return df_out

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

##################################################
# dif, dea, macd
# golden cross followed by macd buy is a good signal
# macd buy is more strong than golden cross
##################################################
def MACD(hisdata, df):
    df_out = df.copy()
    closelist = hisdata['close'] 
        
    # calculate macd index
    dif, dea, half_macd = ta.MACD(closelist.values, fastperiod=12, slowperiod=26, signalperiod=9)
    df_out['DIF'] = dif
    df_out['DEA'] = dea
    df_out['MACD'] = half_macd * 2

    # find golden cross and dead cross
    for i in range(33, hisdata.shape[0]-1):
        old_dif = df_out.loc[i, 'DIF']
        old_dea = df_out.loc[i, 'DEA']
        old_macd = df_out.loc[i, 'MACD']
        new_dif = df_out.loc[i+1, 'DIF']
        new_dea = df_out.loc[i+1, 'DEA']
        new_macd = df_out.loc[i+1, 'MACD']

        if (old_dif <= old_dea) & (new_dif >= new_dea):
            df_out.loc[i+1, 'MACD_cross'] = 'golden'
        if (old_dif >= old_dea) & (new_dif <= new_dea):
            df_out.loc[i+1, 'MACD_cross'] = 'dead'
        if (old_macd > 0.1) and (new_macd > 0.1) and (new_macd > old_macd):
            df_out.loc[i+1, 'MACD_red'] = True
        
    return df_out


def KDJ(hisdata, df):
    df_out = df.copy()
    closelist = hisdata['close'] 
    highlist = hisdata['high']
    lowlist = hisdata['low']

    # calculatei 9 day kdj index
    low_9day = lowlist.rolling(window=9).min() 
    high_9day = highlist.rolling(window=9).max()
    rsv = (closelist - low_9day) / (high_9day - low_9day) * 100
    df_out['K'] = rsv.ewm(com=2).mean()
    df_out['D'] = df_out['K'].ewm(com=2).mean() 
    df_out['J'] = 3 * df_out['K'] - 2 * df_out['D']

    # find golden cross and dead cross
    kdj_position = df_out['K'] > df_out['D'] 
    df_out.loc[kdj_position[(kdj_position == True) & (kdj_position.shift() == False)].index, 'KDJ_cross'] = 'golden' 
    df_out.loc[kdj_position[(kdj_position == False) &
(kdj_position.shift() == True)].index, 'KDJ_cross'] = 'dead'
    return df_out


