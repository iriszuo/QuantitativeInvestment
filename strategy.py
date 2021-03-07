import utils as u
import tech_benchmark as tech
from datetime import datetime, timedelta
import baostock as bs


def strategy(code, date):
    startdate = (datetime.strptime(date, "%Y-%m-%d") + timedelta(-365)).strftime("%Y-%m-%d")
    enddate = date
    hisdata = u.get_his_k_data(code, startdate, enddate)
    df = hisdata[['date']]
    df = tech.CCI(hisdata, df)
    df = tech.KDJ(hisdata, df)
    df = tech.MACD(hisdata, df)

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
    if df.iloc[-1:]['trend'].values[0] == True:
        for i in range(10):
            if df.shift(i).iloc[-1:]['short'].values[0] == True:
                return True
    return False

