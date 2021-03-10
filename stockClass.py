'''
@author: iriszuo 
@description:
    股票主类，可表示某一只股票。类的成员函数包含三种：
    1）以basic开头：表示基本函数，如计算股票涨跌幅等。
    2）以bench开头：表示技术指标函数，如MACD,KDJ。
    3）以strategy开头：表示策略函数。
'''

import pickle
import pandas as pd
import baostock as bs
from baostock_structure import STOCK_DICT
import talib as ta
from datetime import datetime, timedelta
import utils as u
import numpy as np

class Stock():
    ''' 构造函数：从pkl文件中读取该股票的基本数据，存储在类中。
    input:
        code: 股票代码，是类的主要标识。
        dict_all:可选参数，表示全部股票数据字典。如果给出，将从该字典中查找该股票并初始化。
        dict_self:可选参数，表示该股票的数据字典。如果给出，将直接利用该数据初始化。
        如果以上两个参数均不给出，将从本地读取pkl文件，pkl文件的内容即为dict_all。
    output:
        股票类。其中以下成员函数被初始化，它们对应了字典中的key和value：
        code: 股票代码，字符串形式
        name：股票中文名称，字符串形式
        ipodate：上市日期，字符串形式，形如“2020-01-01”。所有日期都是该格式。
        kdata_all：自上市以来的所有k线数据，剔除了停牌日。dataframe二维形式。具体的列标题参见baostock_structure.py中的HISTORY_K_DATA_PLUS
    '''
    def __init__(self, code, dict_all={}, dict_self={}):
        self.code = code
        if (dict_all):
            stock_dict = dict_all[code]
        elif (dict_self):
            stock_dict = dict_self
        else:
            # fetch data from pickle
            f_stocks_kline = open('stock_data_kline.pkl', 'rb')
            stock_dict = pickle.load(f_stocks_kline)[code]
            f_stocks_kline.close()
        self.name = stock_dict[STOCK_DICT.code_name.name]
        self.ipodate = stock_dict[STOCK_DICT.ipoDate.name]
        self.kdata_all = stock_dict[STOCK_DICT.kdata.name]
    
    ''' 获取某段时间的k线数据
    input:
        startdate:开始日期。不需要考虑是否是交易日。
        enddate:结束日期。同上。
    output:
        hisdata:历史k线数据，dataframe格式。
    exception:
        如果startdate<enddate,将抛出异常。
        如果该时间段内均无交易日或停牌，则hisdata为空。
    '''
    def basic_period_hisdata(self, startdate, enddate): 
        assert datetime.strptime(startdate, "%Y-%m-%d") <= datetime.strptime(enddate, "%Y-%m-%d")
        mask = (self.kdata_all['date'] >= startdate) & (self.kdata_all['date'] <= enddate)
        hisdata = self.kdata_all.loc[mask]
        if hisdata.empty:
            return hisdata
        hisdata = hisdata.reset_index(drop=True)
        return hisdata
    
    '''计算某时间段内的股票涨跌幅。
    input:
        startdate:开始日期。不需要考虑是否是交易日。
        enddate:结束日期。同上。
    output:
        gains:该时间段内的涨跌幅。按收盘价计。
    exception:
        如果时间段内无交易日，返回False 
    '''
    def basic_period_stock_gains(self, startdate, enddate):
        hisdata = self.basic_period_hisdata(startdate, enddate)
        if hisdata.empty: # no valid tradeday during the period
            return False
        old_price = float(u.get_df_value(hisdata, 0, 'close'))
        current_price = float(u.get_df_value(hisdata, -1, 'close'))
        gains = (current_price - old_price) / old_price
        return gains


    def bench_k_line_ma(self, hisdata, days):
        df = hisdata[['date']]
        df['MA_' + str(days)] = hisdata['close'].rolling(days).mean()
        return df

    ##################################################
    # dif, dea, macd
    # golden cross followed by macd buy is a good signal
    # macd buy is more strong than golden cross
    ##################################################
    def bench_MACD(self, hisdata):
        df_out = hisdata[['date']]
        closelist = hisdata['close'] 
        
        # calculate macd index
        dif, dea, half_macd = ta.MACD(closelist.values, fastperiod=12, slowperiod=26, signalperiod=9)
        df_out.loc[:,'DIF'] = dif
        df_out.loc[:,'DEA'] = dea
        df_out.loc[:,'MACD'] = half_macd * 2
        df_out.loc[:, 'MACD_cross'] = None
        df_out.loc[:, 'MACD_red'] = None

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


    def bench_KDJ(self, hisdata):
        df_out = hisdata[['date']]
        closelist = hisdata['close'] 
        highlist = hisdata['high']
        lowlist = hisdata['low']

        # calculatei 9 day kdj index
        low_9day = lowlist.rolling(window=9).min() 
        high_9day = highlist.rolling(window=9).max()
        rsv = (closelist - low_9day) / (high_9day - low_9day) * 100
        df_out.loc[:,'K'] = rsv.ewm(com=2).mean()
        df_out.loc[:,'D'] = df_out['K'].ewm(com=2).mean() 
        df_out.loc[:,'J'] = 3 * df_out['K'] - 2 * df_out['D']

        # find golden cross and dead cross
        kdj_position = df_out['K'] > df_out['D'] 
        df_out.loc[:, 'KDJ_cross'] = None
        df_out.loc[kdj_position[(kdj_position == True) & (kdj_position.shift() == False)].index, 'KDJ_cross'] = 'golden' 
        df_out.loc[kdj_position[(kdj_position == False) &
(kdj_position.shift() == True)].index, 'KDJ_cross'] = 'dead'
        return df_out

    ####################################################
    # calculate multiple stocks cci for a specific period
    # cci > 100/ cci < -100 but change direction: buy
    # cci < -100/ cci > 100 but change direction: sell
    ####################################################
    def bench_CCI(self, hisdata):
        df_out = hisdata[['date']]
        highlist = hisdata['high'] 
        lowlist = hisdata['low']
        closelist = hisdata['close'] 
        
        CCIlist = ta.CCI(highlist,lowlist,closelist) # default timeperiod=14, means use 14 days mean average
        CCIlist = list(CCIlist)
        df_out.loc[:, 'CCI_14'] = CCIlist
        return df_out


    def strategy_macd_kdj_cci(self, date):
        # use one year data to calculate index
        startdate = (datetime.strptime(date, "%Y-%m-%d") + timedelta(-365)).strftime("%Y-%m-%d")
        enddate = date

        hisdata = self.basic_period_hisdata(startdate, enddate)
        if hisdata.empty:
            return False 
        df = hisdata[['date']]
        df = u.join_df_column(df, self.bench_CCI(hisdata), 'date')
        df = u.join_df_column(df, self.bench_KDJ(hisdata), 'date')
        df = u.join_df_column(df, self.bench_MACD(hisdata), 'date')

        # apply short benchmark strategy
        j_value = df['J'] < 0
        j_direction = df['J'] > df.shift()['J']
        cci_value = df['CCI_14'] < -100
        cci_direction = df['CCI_14'] > df.shift()['CCI_14']
        df.loc[df[(j_value==True) & (j_direction==True) & (cci_value==True) & (cci_direction==True) ].index, 'short'] = True

        # apply trend benchmark strategy
        macd_up = (df['MACD_cross'] == 'golden') & (df['MACD'] > 0)
        macd_down = (df.shift()['MACD_cross'] == 'golden') & (df['MACD_red']==True)
        df.loc[df[(macd_up==True) | (macd_down==True)].index, 'trend'] = True
    
        # in 10 tradedays, sequantially occur short buy and trend buy
        if u.get_df_value(df, -1, 'trend') == True:
            for i in range(10):
                if u.get_df_value(df.shift(i), -1, 'short') == True:
                    return True
        return False


    def backtest(self, strategy, holddays, startdate, enddate):
        startdate_t = datetime.strptime(startdate, "%Y-%m-%d")
        enddate_t = datetime.strptime(enddate, "%Y-%m-%d")
        test_cnt = 0    # how many days are tested
        buy_cnt = 0     # how many days have buy signal
        buy_success = 0 # how many buy signal is succussful (gain>10% in holddays)
        max_gain_list=[]
        min_gain_list=[]
        avg_max_gain = None
        avg_min_gain = None

        for date in range((enddate_t - startdate_t).days + 1):
            date = startdate_t + timedelta(date)
            date = date.strftime("%Y-%m-%d")
            if not u.is_tradeday(date):
                continue
            
            test_cnt = test_cnt + 1
            is_buy = strategy(date)
            if is_buy:
                buy_cnt = buy_cnt + 1
                gain_list = []
                begin_date = date
                for days in range(1, holddays+1):
                    end_date = (datetime.strptime(date, "%Y-%m-%d") + timedelta(days=days)).strftime("%Y-%m-%d")
                    gain = self.basic_period_stock_gains(begin_date, end_date)
                    # skip no tradeday
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


