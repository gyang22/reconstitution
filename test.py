import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
from datetime import timedelta
import numpy as np

ticker = "USFD"
start_date = "2016-05-27"
end_date = "2016-05-31"
data = yf.download(ticker, start=start_date, end=end_date)['Adj Close']
returns = data.pct_change().dropna()
mean = returns.mean()
daily_volatility = returns.std()
print(len(data))
print(returns)
print(mean)
print(daily_volatility)


results = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.011538461538461539, 0.011363636363636364, 0.4521072796934866, 0.5348837209302325, 0.5155038759689923, 0.4708171206225681, 0.4897959183673469, 0.5431034482758621, 0.5150214592274678, 0.5596707818930041, 0.5495867768595041, 0.5755102040816327, 0.6307053941908713, 0.6371308016877637, 0.6538461538461539, 0.6652173913043479, 0.7017543859649122, 0.6096491228070176, 0.5964912280701754, 0.5963302752293578, 0.6037735849056604]
ranking_results = [[0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.4559386973180077, 0.5348837209302325, 0.5155038759689923, 0.4708171206225681, 0.4816326530612245, 0.5431034482758621, 0.5107296137339056, 0.5596707818930041, 0.5495867768595041, 0.5795918367346938, 0.6473029045643154, 0.6329113924050633, 0.6538461538461539, 0.6608695652173913, 0.706140350877193, 0.6096491228070176, 0.5964912280701754, 0.6055045871559633, 0.5990566037735849]]

historical_constituents = pd.read_csv("data/MGC_constituents.csv")

earliest_date = pd.to_datetime(historical_constituents.iloc[0]['EndTime'])
latest_date = pd.to_datetime(historical_constituents.iloc[-1]['EndTime'])

result_dates = [d for d in pd.date_range(start=earliest_date, end=latest_date, freq='Q').to_list()]
backtesting_dates = [d - timedelta(days=30) for d in pd.date_range(start=earliest_date, end=latest_date, freq='Q').to_list()]

print(len(results))
print(len(backtesting_dates))

print(np.mean(results))

print(np.array(results) - np.array(ranking_results))