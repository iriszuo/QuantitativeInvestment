# 股票量化投资
## 代码说明
1. get_stock_basic.py 拉取当前市场的所有股票，以及他们的上市日期、自ipo至今的所有收盘价数据，存放于字典结构，存放于pickle文件。
2. stockClass.py 股票主类，使用pickle中的data初始化。成员函数包含三类：基本类以basic开头，指标类以bench开头，策略类以strategy开头，还包括一个回测函数backtest。
3. utils.py 辅助函数
4. test.py 测试策略的回测功能
## 指标
已经迁移的指标
1. MACD
2. KDJ
3. CCI
还需迁移的指标（从tech_benchmark.py迁移到stockClass中）
1. RPS
2. RSI
## 策略
1. 趋势指标MACD+快速指标KDJ,CCI。MACD线上金叉/线下金叉且红柱放大+快速指标显示超卖且转向，发出买入信号。
