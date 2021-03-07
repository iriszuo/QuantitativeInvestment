import baostock as bs
import utils as u

code = "sh.600000"
startdate = "2015-01-01"
enddate = "2016-01-01"


bs.login()
stock_dict = u.fetch_histkdata(code = code)
stock = Stock(code, dict_self=stock_dict)
buycnt, buysucc, avgmax, avgmin = stock.backtest(self.strategy_macd_kdj_cci, 15, startdate, enddate)
print('buycnt, buysucc, avgmax, avgmin')
bs.logout()
