import pandas as pd
import yfinance as yf
from datetime import datetime
from datetime import timedelta
from mcmc import MCMCIndexPredictor
import time

start_time = time.time()


index_ticker = "MGC"


historical_constituents = pd.read_csv("data/MGC_constituents.csv")

earliest_date = pd.to_datetime(historical_constituents.iloc[0]['EndTime'])
latest_date = pd.to_datetime(historical_constituents.iloc[-1]['EndTime'])

result_dates = [d for d in pd.date_range(start=earliest_date, end=latest_date, freq='Q').to_list()]
backtesting_dates = [d for d in pd.date_range(start=earliest_date, end=latest_date, freq='Q').to_list()]


filtered_companies = pd.read_csv("data/CRSP_filtered_companies.csv")

model = MCMCIndexPredictor(universe=filtered_companies, num_days=1, num_simulations=10000, look_back_days=15)

model_results = []
for date in backtesting_dates:
    index_probabilities = model.predict(date)
    print(index_probabilities)
    top_mega_companies = index_probabilities[index_probabilities['Mega'] >= 
            index_probabilities.drop(columns=['Mega']).max(axis=1)].index.tolist()
    model_results.append(set(top_mega_companies))


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
for model_result, historical_result in zip(model_results, historical_results):
    accuracy_results.append(len(model_result.intersection(historical_result)) / len(historical_result))

print(accuracy_results)

end_time = time.time()

print(f"Runtime: {end_time - start_time} seconds.")
