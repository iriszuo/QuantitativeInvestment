# tushare token: 89b3a4a7b139deae60a017503c40fee4bd88d8b28a5ca7b0dda1b5e8

import pandas as pd  
import tushare as ts 
import matplotlib.pyplot as plt

from pylab import mpl
mpl.rcParams['font.sans-serif']=['SimHei']
mpl.rcParams['axes.unicode_minus']=False

token='89b3a4a7b139deae60a017503c40fee4bd88d8b28a5ca7b0dda1b5e8'
ts.set_token(token)
pro=ts.pro_api()

df = pro.stock_basic(exchange='', list_status='L', fields='ts_code,symbol,name,area,industry,list_date')qwertyuiop
print(df)