from yahoo_fin import stock_info as si
import yfinance as yf
import pandas as pd
import time
import concurrent.futures
import queue


parallel = True


start_time = time.time()

'''
Gather the list of tickers from yahoo_fin.
'''

sp500_tickers = si.tickers_sp500()
nasdaq_tickers = si.tickers_nasdaq()
dow_tickers = si.tickers_dow()
other_tickers = si.tickers_other()


all_tickers = list(set(sp500_tickers + nasdaq_tickers + dow_tickers + other_tickers))
all_tickers = [s for s in all_tickers if s.strip()]
num_tickers = len(all_tickers)
counter = 0

print(f"Total number of unique tickers: {num_tickers}")


'''
Check yfinance for ticker data and add it to the table.
'''

market_cap_unavailable = 0

errored = 0

def delayed_fetch(ticker):
    time.sleep(0.5)
    return fetch_stock_info(ticker)

def fetch_stock_info(ticker):
    global counter, market_cap_unavailable
    try:
        stock = yf.Ticker(ticker)
        stock_info = stock.info
        market_cap = stock_info.get('marketCap', 'N/A')
        if market_cap != 'N/A':
            counter += 1
            print(f"Found data for {ticker}.")
            return (stock_info, 1)
        else:
            #print(f"Market cap not available for {ticker}.")
            market_cap_unavailable += 1
            counter += 1
            return (ticker, 2)
    except Exception as e:
        #print(f"Error fetching data for {ticker}")
        return (ticker, 0)
    

data = []
error_tickers = queue.Queue()

error_counter = {}

def worker():
    global error_counter, counter
    while True:
        try:
            ticker = error_tickers.get(timeout=5)
        except queue.Empty:
            return
        if ticker is None:
            break
        result = fetch_stock_info(ticker)
        if result[1] == 1:
            data.append(result[0])
        elif result[1] == 0:
            if error_counter.get(result[0], 0) <= 10:
                print(f"Number of errors for {result[0]}: {error_counter.get(result[0], 0)} / {10}")
                error_tickers.put(result[0])
            error_counter[result[0]] = error_counter.get(result[0], 0) + 1
        print(f"Queue size: {error_tickers.qsize()}")
        error_tickers.task_done()
        time.sleep(0.5)



if parallel:
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_to_ticker = {executor.submit(delayed_fetch, ticker): ticker for ticker in all_tickers}
        for i, future in enumerate(concurrent.futures.as_completed(future_to_ticker)):
            if i % 10 == 0:
                print(f"Checking {i} / {num_tickers}")
            result = future.result()
            if result[1] == 1:
                data.append(result[0])
            elif result[1] == 0:
                error_tickers.put(result[0])
                
    errored = error_tickers.qsize()
    counter = 0

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(worker) for _ in range(5)]

        for future in concurrent.futures.as_completed(futures):
            future.result()

else:
    for i, ticker in enumerate(all_tickers):
        if i % 10 == 0:
            print(f"{i} / {num_tickers}")
        try:
            stock = yf.Ticker(ticker)
            stock_info = stock.info
            market_cap = stock_info.get('marketCap', 'N/A')
            if market_cap != 'N/A':
                data.append(stock_info)
        except Exception as e:
            print(f"Error fetching data for {ticker}: {e}")
            error_tickers.append(ticker)
    while len(error_tickers) > 0:
        print(f"Remaining tickers to check: {len(error_tickers)}")
        ticker = error_tickers.pop()
        try:
            stock = yf.Ticker(ticker)
            stock_info = stock.info
            market_cap = stock_info.get('marketCap', 'N/A')
            if market_cap != 'N/A':
                data.append(stock_info)
        except Exception as e:
            print(f"Error fetching data for {ticker}: {e}")
            error_tickers.append(ticker)



df = pd.DataFrame(data)
print("Table created.")
df = df.sort_values(by='marketCap', ascending=False).reset_index(drop=True)


top_companies = df.head(10)
print(top_companies)

df.to_csv("top_companies.csv")

end_time = time.time()

print(f'Data collection took {end_time - start_time} seconds to complete.')
print(f"Total of {market_cap_unavailable} / {num_tickers} non-available market cap tickers.")
