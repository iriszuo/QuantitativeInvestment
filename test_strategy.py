import numpy as np
import pandas as pd
import baostock as bs
from datetime import datetime, timedelta
import utils as u
import tech_benchmark as tech

'''##########################
# 1. 超买超卖信息
Old:
J<0
CCI<-200
new:
J increase
CCI increase
2. 趋势信息
macd线上金叉  或者
Macd线下金叉叠加红柱放量
3. 30日线多头排列
########################
'''
startdate = "2020-01-01"
enddate = "2021-01-01"
stock_list = u.load_stock_from_csv()
bs.login()
for stock in stock_list:
    hisdata = u.get_his_k_data(stock, startdate, enddate)
    df = hisdata[['date']]
    df = tech.CCI(hisdata, df)
    df = tech.KDJ(hisdata, df)
    df = tech.MACD(hisdata, df)

    j_value = df['J'] < 0
    j_direction = df['J'] > df.shift()['J']
    cci_value = df['CCI_14'] < -100
    cci_direction = df['CCI_14'] > df.shift()['CCI_14']
    df.loc[df[(j_value==True) & (j_direction==True) & (cci_value==True) & (cci_direction==True) ].index, 'short'] = True

    macd_up = (df['MACD_cross'] == 'golden') & (df['MACD'] > 0)
    macd_down = (df.shift()['MACD_cross'] == 'golden') & (df['MACD_red']==True)
    df.loc[df[(macd_up==True) | (macd_down==True)].index, 'trend'] = True
    print(df)
    df.to_csv("./test_strategy.csv", encoding="utf-8", index=False)
    break
bs.logout()
