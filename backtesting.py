import pandas as pd
import yfinance as yf

index_ticker = "AAPL"


ticker = yf.Ticker(index_ticker)

print(ticker.info)
