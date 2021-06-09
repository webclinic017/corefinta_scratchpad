import math
import numpy as np
from finta import TA
import yfinance as yf
import plotly.graph_objects as go
import plotly.express as px

import pandas as pd

from datetime import datetime

""" do WMA 21 n = 5 ATR = 21"""

ticker = "NQ=F"
data = yf.download(tickers = ticker, start='2016-01-04', end='2021-06-04')
# data = yf.download(tickers = ticker, period = "1y")

# valid periods: 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max
# valid intervals: 1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo
# https://pypi.org/project/yfinance/
# data = yf.download("SPY AAPL", start="2017-01-01", end="2017-04-30")

df1 = pd.DataFrame(data)

# print(df1)

df = df1.reset_index()

# print(df)

df7 = df.rename(columns = {'Date': 'date', 'Open':'open', 'High': 'high', 'Low':'low', 'Close':'close','Volume': 'volume'}, inplace = False)

# print(df7)
df7.to_csv('daily.csv')

n = 5

df3 = df7.groupby(np.arange(len(df7))//n).max()
# print('df3 max:', df3)

df4 = df7.groupby(np.arange(len(df7))//n).min()
# print('df4 min:', df4)

df5 = df7.groupby(np.arange(len(df7))//n).first()
# print('df5 open:', df5)

df6 = df7.groupby(np.arange(len(df7))//n).last()
# print('df6 close:', df6)


agg_df = pd.DataFrame()

agg_df['date'] = df6['date']
agg_df['low'] = df4['low']
agg_df['high'] = df3['high']
agg_df['open'] = df5['open']
agg_df['close'] = df6['close']

# print(agg_df)

df2 = agg_df

# print(df2)
num_periods = 21
df2['SMA'] = TA.SMA(df2, 21)
df2['FRAMA'] = TA.FRAMA(df2, 10)
df2['WMA'] = TA.WMA(df2, 21)
df2['TEMA'] = TA.TEMA(df2, num_periods)
# df2['VWAP'] = TA.VWAP(df2)

# how to get previous row's value
# df2['previous'] = df2['lower_band'].shift(1)

# ATR

# https://www.statology.org/exponential-moving-average-pandas/
num_periods_ATR = 21
multiplier = 1

df2['ATR_diff'] = df2['high'] - df2['low']
df2['ATR'] = df2['ATR_diff'].ewm(span=num_periods_ATR, adjust=False).mean()
# df2['ATR'] = df2['ATR_diff'].rolling(window=num_periods_ATR).mean()
df2['Line'] = df2['WMA']
df2['upper_band'] = df2['Line'] + multiplier * df2['ATR']
df2['lower_band'] = df2['Line'] - multiplier * df2['ATR']

multiplier_1 = 1.6
multiplier_2 = 1.4

df2['upper_band_1'] = df2['Line'] + multiplier_1 * df2['ATR']
df2['lower_band_1'] = df2['Line'] - multiplier_1 * df2['ATR']

df2['upper_band_2'] = df2['Line'] + multiplier_2 * df2['ATR']
df2['lower_band_2'] = df2['Line'] - multiplier_2 * df2['ATR']

# previous figures
# df2['upper_band_1_prev'] = df2['upper_band_1'].shift(1)
# df2['lower_band_1_prev'] = df2['lower_band_1'].shift(1)
# df2['upper_band_1_diff'] = df2['upper_band_1'] - df2['upper_band_1_prev']
# df2['lower_band_1_diff'] = df2['lower_band_1'] - df2['lower_band_1_prev']
# df2['upper_band_1_proj'] = df2['upper_band_1'] + df2['upper_band_1_diff']
# df2['lower_band_1_proj'] = df2['lower_band_1'] + df2['lower_band_1_diff']
# df2.loc[len(df2), 'lower_band_1'] = df2.loc[len(df2)-1, 'lower_band_1_proj']

# try the loop again

i = df2.index[-1]
print(i)
bars_back = 2
upper_band_1_diff = df2.loc[len(df2)-1, 'upper_band_1'] - df2.loc[len(df2)-bars_back, 'upper_band_1']
lower_band_1_diff = df2.loc[len(df2)-1, 'lower_band_1'] - df2.loc[len(df2)-bars_back, 'lower_band_1']
date_diff = df2.loc[len(df2)-1, 'date'] - df2.loc[i-bars_back, 'date']
line_diff = df2.loc[len(df2)-1, 'Line'] - df2.loc[i-bars_back, 'Line']
# atr_proj = df2.iloc[len(df2)-1, 'ATR']
print(date_diff)
print(line_diff)
# print(atr_proj)

# upper_band_1_proj = df2.loc[len(df2)-1, 'upper_band_1'] + upper_band_1_diff
# df2.loc[len(df2), 'upper_band_1'] = upper_band_1_proj

counter = 0
while counter < 30:
    df2.loc[len(df2), 'Line'] = df2.loc[len(df2)-1, 'Line'] + line_diff
    df2.loc[len(df2)-1, 'date'] = df2.loc[len(df2)-2, 'date'] + date_diff
    df2['upper_band_1'] = df2['Line'] + df2.loc[len(df2)-3, 'ATR'] * multiplier_1
    counter += 1

# https://stackoverflow.com/questions/16096627/selecting-a-row-of-pandas-series-dataframe-by-integer-index
# https://stackoverflow.com/questions/15862034/access-index-of-last-element-in-data-frame

# df2.loc[len(df2), 'upper_band_1'] = df2.loc[len(df2) - 1, 'upper_band_1'] + upper_band_1_diff
# df2.loc[len(df2) - 1, 'lower_band_1'] = df2.loc[len(df2) - 2, 'lower_band_1'] + lower_band_1_diff  # make sure this is one row higher
# df2.loc[len(df2) - 2, 'date'] = df2.loc[len(df2) - 3, 'date'] + date_diff
# df2.loc[len(df2) - 3, 'Line'] = df2.loc[len(df2) - 4, 'Line'] + line_diff

# append dataframe
# https://stackoverflow.com/questions/53304656/difference-between-dates-between-corresponding-rows-in-pandas-dataframe
# https://www.geeksforgeeks.org/how-to-add-one-row-in-an-existing-pandas-dataframe/
# https://stackoverflow.com/questions/10715965/create-pandas-dataframe-by-appending-one-row-at-a-time
# https://stackoverflow.com/questions/49916371/how-to-append-new-row-to-dataframe-in-pandas
# https://stackoverflow.com/questions/50607119/adding-a-new-row-to-a-dataframe-why-loclendf-instead-of-iloclendf
# https://stackoverflow.com/questions/31674557/how-to-append-rows-in-a-pandas-dataframe-in-a-for-loop


print(df2[['date','upper_band_1','lower_band_1']].tail(25))
print(df2.tail(25))

df2.to_csv("gauss.csv")

# https://community.plotly.com/t/how-to-plot-multiple-lines-on-the-same-y-axis-using-plotly-express/29219/9

# https://plotly.com/python/legend/#legend-item-names

# fig1 = px.scatter(df2, x='date', y=['close', 'open', 'high', 'low'], title='SPY Daily Chart')

fig1 = go.Figure(data=[go.Candlestick(x=df2['date'],
                open=df2['open'],
                high=df2['high'],
                low=df2['low'],
                close=df2['close'])]

)

fig1.add_trace(
    go.Scatter(
        x=df2['date'],
        y=df2['upper_band'],
        name='upper band',
        mode="lines",
        line=go.scatter.Line(color="gray"),
        showlegend=True)
)

fig1.add_trace(
    go.Scatter(
        x=df2['date'],
        y=df2['lower_band'],
        name='lower band',
        mode="lines",
        line=go.scatter.Line(color="gray"),
        showlegend=True)
)

fig1.add_trace(
    go.Scatter(
        x=df2['date'],
        y=df2['upper_band_1'],
        name='upper band_1',
        mode="lines",
        line=go.scatter.Line(color="gray"),
        showlegend=True)
)

fig1.add_trace(
    go.Scatter(
        x=df2['date'],
        y=df2['lower_band_1'],
        name='lower band_1',
        mode="lines",
        line=go.scatter.Line(color="gray"),
        showlegend=True)
)


fig1.add_trace(
    go.Scatter(
        x=df2['date'],
        y=df2['Line'],
        name="WMA",
        mode="lines",
        line=go.scatter.Line(color="blue"),
        showlegend=True)
)

fig1.show()

