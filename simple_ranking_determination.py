import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

historical_constituents = pd.read_csv("data/MGC_constituents.csv")

earliest_date = pd.to_datetime(historical_constituents.iloc[0]['EndTime'])
latest_date = pd.to_datetime(historical_constituents.iloc[-1]['EndTime'])

result_dates = [d for d in pd.date_range(start=earliest_date, end=latest_date, freq='Q').to_list()]
backtesting_dates = [d - timedelta(days=30) for d in pd.date_range(start=earliest_date, end=latest_date, freq='Q').to_list()]


filtered_companies = pd.read_csv("data/CRSP_filtered_companies.csv")

ranking_results = []
num_dates = len(backtesting_dates)
for j, date in enumerate(backtesting_dates):
    print(date)
    market_caps = {}
    total_length = len(filtered_companies['symbol'].unique())
    for i, ticker in enumerate(filtered_companies['symbol'].unique()):
        print(f"Date {j + 1} / {num_dates}... downloading {i + 1} / {total_length}...")
        hist = yf.download(ticker, start=datetime.strftime(date - timedelta(days=10), '%Y-%m-%d'), 
                           end=datetime.strftime(date + timedelta(days=1), '%Y-%m-%d'))
        if not hist.empty:
            adj_close_price = hist['Adj Close'].iloc[-1]
        else:
            continue
        market_caps[ticker] = adj_close_price * filtered_companies.loc[filtered_companies[
                'symbol'] == ticker, 'sharesOutstanding'].values[0]
    
    sorted_market_caps = sorted(market_caps.items(), key=lambda x: x[1], reverse=True)
    total_market_cap = sum(market_caps.values())
    cumulative_cap = 0
    top_70_percent_companies = []
    for ticker, cap in sorted_market_caps:
        cumulative_cap += cap
        top_70_percent_companies.append(ticker)
        if (cumulative_cap + 0.5 * cap) / total_market_cap >= 0.70:
            break
    ranking_results.append(set(top_70_percent_companies))


historical_results = []
for date in result_dates:
    constituents = set()
    day_delta = 0
    while len(constituents) == 0:
        constituents = set(historical_constituents[
            historical_constituents['EndTime'] == (date + timedelta(days=day_delta)).strftime('%Y-%m-%d')]['Symbol'].unique())
        day_delta += 1
    historical_results.append(set([s.split(" ")[0] for s in constituents]))


accuracy_results = []
for ranking_result, historical_result in zip(ranking_results, historical_results):
    accuracy_results.append(len(ranking_result.intersection(historical_result)) / len(historical_result))

print(accuracy_results)