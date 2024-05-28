import pandas as pd
import yfinance as yf
from datetime import datetime
from datetime import timedelta
from mcmc import MCMCIndexPredictor


index_ticker = "MGC"


historical_constituents = pd.read_csv("data/MGC_constituents.csv")

earliest_date = pd.to_datetime(historical_constituents.iloc[0]['EndTime'])
latest_date = pd.to_datetime(historical_constituents.iloc[-1]['EndTime'])

result_dates = [d + timedelta(days=3) for d in pd.date_range(start=earliest_date, end=latest_date, freq='Q').to_list()]
backtesting_dates = [d - timedelta(days=30) for d in pd.date_range(start=earliest_date, end=latest_date, freq='Q').to_list()]


filtered_companies = pd.read_csv("data/CRSP_filtered_companies.csv").head(10)

model = MCMCIndexPredictor(universe=filtered_companies, num_days=30, num_simulations=10000)

results = []
for date in backtesting_dates:
    print(date)
    results.append(model.predict(date))

print(results)


 




