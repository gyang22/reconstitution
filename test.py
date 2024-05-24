import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt


def data_on_date(ticker, date):
    stock = yf.Ticker(ticker)
    historical_data = stock.history(start=date, end=date)
    if not historical_data.empty:
        return historical_data



spy_historical_constituents = pd.read_csv("SPY_constituents.csv")

spy_historical_constituents = spy_historical_constituents.drop_duplicates()

unique_dates = spy_historical_constituents['EndTime'].unique()

ticker_appearances = {}

for date in unique_dates:
    print(date)
    current_constituents = spy_historical_constituents[spy_historical_constituents['EndTime'] == date]
    for ticker in current_constituents['Symbol'].unique():
        ticker_appearances[ticker] = ticker_appearances.get(ticker, 0) + 1

