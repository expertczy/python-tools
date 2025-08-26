import yfinance as yf
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

# 时间范围
end_date = datetime.today()
start_date = end_date - timedelta(days=280)

# 设置数据间隔
interval = '1d'

# 设置要突出显示的日期 (示例：使用一个特定日期)
show_highlight_date = False  # 设置为True开启垂直线，False关闭
highlight_date = datetime(2025, 3, 4)  # 你可以修改这个日期

# 指数及代码
indices = {
    # 'short qqq':'SQQQ',
    'qqq':'qqq',
    # 'pltr short':'spl3.L',
    # 'pltr': 'PLTR',
    'S&P 500': '^GSPC',
    # 'Nasdaq': '^IXIC',
    # 'Dow Jones': '^DJI',
    'FTSE 100': '^FTSE',
    'Nikkei 225': '^N225',
    # 'VUAG': 'VUAG.L',
    'all world':'^990100-USD-STRD',
    # 'equal':'RSP',
    # 'jpmorgan':'JAM.L',
    # 'vusa':'VUSA.L',
    # 'spxl':'SPXL.L',
    # 'VUG':'VUG',
    # 'qqq':'qqq',
    # 'IITU.L':'IITU.L',
    # 'IWF':'IWF',
}

data_dict = {}
for name, ticker in indices.items():
    print(f"正在下载 {name} 数据...")
    df = yf.download(ticker, start=start_date, end=end_date, interval=interval)
    if not df.empty:
        price_column = 'Adj Close' if 'Adj Close' in df.columns else 'Close'
        # 计算百分比变化
        data_dict[name] = (df[price_column] - df[price_column].iloc[0]) / df[price_column].iloc[0] * 100

# 绘制折线图
plt.figure(figsize=(14, 8))
for name, series in data_dict.items():
    plt.plot(series.index, series, label=name)

# 添加垂直线来突出显示特定日期
if show_highlight_date:
    plt.axvline(x=highlight_date, color='r', linestyle='--', alpha=0.5, label='Highlight Date')

# 图表美化
plt.title("Price")
plt.xlabel("Date")
plt.ylabel("Change (%)")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()
