from yahoo_fin import stock_info as si
import yfinance as yf
import pandas as pd
import time

start_time = time.time()

sp500_tickers = si.tickers_sp500()
nasdaq_tickers = si.tickers_nasdaq()
dow_tickers = si.tickers_dow()
other_tickers = si.tickers_other()


all_tickers = list(set(sp500_tickers + nasdaq_tickers + dow_tickers + other_tickers))
num_tickers = len(all_tickers)

print(f"Total number of unique tickers: {num_tickers}")


data = []


for i, ticker in enumerate(all_tickers):
    print(f"{i} / {num_tickers}")
    try:
        stock = yf.Ticker(ticker)
        stock_info = stock.info
        market_cap = stock_info.get('marketCap', 'N/A')
        if market_cap != 'N/A':
            data.append(stock_info)
            
        else:
            print(f"Market cap not available for {ticker}.")
    except Exception as e:
        print(f"Error fetching data for {ticker}: {e}")


df = pd.DataFrame(data)
df = df.sort_values(by='marketCap', ascending=False).reset_index(drop=True)


top_companies = df.head(10)
print(top_companies)

df.to_csv("top_companies.csv")

end_time = time.time()

print(f'Data collection took {end_time - start_time} to complete.')
