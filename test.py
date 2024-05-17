import requests
import yfinance as yf
import pandas as pd


api_key = "4MHMP7DK6V0HBRIO"
ticker = "AMZN"

url = f'https://www.alphavantage.co/query?function=OVERVIEW&symbol={ticker}&apikey={api_key}'
# r = requests.get(url)
# data = r.json()



def get_market_cap(ticker):
    try:
        stock = yf.Ticker(ticker)
        market_cap = stock.info['marketCap']
        return market_cap
    except KeyError:
        return None

sp500_constituents = pd.read_csv("constituents.csv")

tickers = sp500_constituents["Symbol"].to_list()

for ticker in tickers:
    pass