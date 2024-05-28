import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import yfinance as yf
import time
import plotly.express as px
import plotly.graph_objects as go
from datetime import timedelta
from datetime import datetime



class MCMCIndexPredictor:

    breakpoints = {
        'Mega': 0.70,
        'Mid': 0.85,  
        'Small': 0.98,  
        'Micro': 1.00  
    }
    
    def __init__(self, universe: pd.DataFrame, num_days: int, num_simulations: int):
        self.universe = universe
        self.num_days = num_days
        self.num_simulations = num_simulations

    
    def get_historical_data(self, start_date, end_date):
        historical_data = {}
        for ticker in list(self.universe['symbol'].unique()):
            try:
                data = yf.download(ticker, start=start_date, end=end_date)['Adj Close']
                if not data.empty and len(data) > 1:
                    historical_data[ticker] = data
                    print(f"Data found for {ticker}.")
                else:
                    print(f"No data for {ticker}.")
            except Exception as e:
                print(f"Error occurred downloading data for {ticker}: {e}")
        
        return historical_data

    def find_mu_sigma(self, historical_data):
        daily_returns = {}
        for ticker, data in historical_data.items():
            if not data.empty:
                daily_returns[ticker] = data.pct_change().dropna()

        mean_daily_returns = {}
        daily_volatility = {}

        for ticker, returns in daily_returns.items():
            mean_daily_returns[ticker] = returns.mean()
            daily_volatility[ticker] = returns.std()
            if np.isnan(daily_volatility[ticker]):
                daily_volatility[ticker] = 0.0

        return pd.Series(mean_daily_returns), pd.Series(daily_volatility)


    def possible_price_paths(self, current_price, mu, sigma, num_days, num_simulations):
        # initiate price movement paths
        dt = 1 / num_days
        price_paths = np.zeros((num_days, num_simulations))
        price_paths[0] = current_price

        # simulate movements
        for t in range(1, num_days):
            rand = np.random.normal(0, 1, num_simulations)
            price_paths[t] = price_paths[t - 1] * np.exp((mu - 0.5 * sigma**2) * dt + sigma * np.sqrt(dt) * rand)
        
        return price_paths
    
    def simulate_market_cap_movement(self, historical_data, mean_daily_returns, daily_volatility):
        simulated_prices = {}
        for ticker in historical_data.keys():
            current_price = historical_data[ticker].iloc[-1]
            mu = mean_daily_returns[ticker]
            sigma = daily_volatility[ticker]

            simulated_prices[ticker] = self.possible_price_paths(current_price=current_price, mu=mu, sigma=sigma, 
                                                            num_days=self.num_days, num_simulations=self.num_simulations)

        simulated_market_caps = {}
        for ticker, prices in simulated_prices.items():
            if np.isnan(prices[-1]).any():
                print(ticker)
                print(prices[-1])
                raise Exception("prices is nan")
            if np.isnan(self.universe.loc[self.universe[
                'symbol'] == ticker, 'sharesOutstanding'].values[0]):
                print(ticker)
                print(self.universe.loc[self.universe[
                'symbol'] == ticker, 'sharesOutstanding'].values)
                raise Exception("shares oustanding nan")
            simulated_market_caps[ticker] = prices[-1] * self.universe.loc[self.universe[
                'symbol'] == ticker, 'sharesOutstanding'].values[0]
            
        return simulated_market_caps
            
    def assign_index(self, market_caps, breakpoints):
        sorted_companies = sorted(market_caps.items(), key=lambda x: x[1], reverse=True)
        total_market_cap = sum(market_caps.values())
        cumulative_cap = 0
        
        assignments = {}
        for company, cap in sorted_companies:
            cumulative_cap_score = (cumulative_cap + 0.5 * cap) / total_market_cap
            cumulative_cap += cap
            if cumulative_cap_score <= breakpoints['Mega']:
                index = 'Mega'
            elif cumulative_cap_score <= breakpoints['Mid']:
                index = 'Mid'
            elif cumulative_cap_score <= breakpoints['Small']:
                index = 'Small'
            else:
                index = 'Micro'
            assignments[company] = index
        
        
        return assignments
    
    def find_index_probabilities(self, simulated_market_caps):
        assignments_list = []
        for i in range(self.num_simulations):
            simulated_caps = {ticker: market_caps[i] for ticker, market_caps in simulated_market_caps.items()}
            assignments = self.assign_index(simulated_caps, self.breakpoints)
            assignments_list.append(assignments)


        assignment_counts = pd.DataFrame(assignments_list).apply(pd.Series.value_counts).fillna(0)
        assignment_probabilities = assignment_counts / self.num_simulations

        restructured_probabilities = assignment_probabilities.T

        return restructured_probabilities
    
    def predict(self, current_date):
        end_date = current_date.strftime('%Y-%m-%d')
        start_date = (current_date - timedelta(days=15)).strftime('%Y-%m-%d')
        historical_data = self.get_historical_data(start_date, end_date)

        mean_daily_returns, daily_volatility = self.find_mu_sigma(historical_data)
    
        simulated_market_caps = self.simulate_market_cap_movement(historical_data, mean_daily_returns, daily_volatility)
        

        results = self.find_index_probabilities(simulated_market_caps)

        return results
    



def plot_assignment_probabilities(assignment_probabilities: pd.DataFrame):
    # Prepare data for Plotly
    prob_data = []
    for ticker in assignment_probabilities.index:
        for index, prob in assignment_probabilities.loc[ticker].items():
            prob_data.append({
                'Ticker': ticker,
                'Index': index,
                'Probability': prob
            })

    prob_df = pd.DataFrame(prob_data)

    # Create a bar plot with Plotly
    fig = go.Figure()

    for ticker in prob_df['Ticker'].unique():
        fig.add_trace(go.Bar(
            x=prob_df[prob_df['Ticker'] == ticker]['Index'],
            y=prob_df[prob_df['Ticker'] == ticker]['Probability'],
            name=ticker
        ))

    fig.update_layout(
        title='Probability of Index Assignment for Each Company',
        xaxis=dict(
            title='Index',
            type='category'
        ),
        yaxis=dict(
            title='Probability'
        ),
        barmode='group',
        xaxis_tickangle=-45,
        margin=dict(l=0, r=0, t=50, b=100),
        height=600,
        width=250 * (len(assignment_probabilities.columns) / 4)  # Adjust width based on number of tickers
    )

    fig.show()


if __name__ == "__main__":

    start_time = time.time()

    filtered_companies = pd.read_csv("data/CRSP_filtered_companies.csv")


    model = MCMCIndexPredictor(filtered_companies, 30, 1000)
    print(model.predict(datetime.strptime("2016-05-31", '%Y-%m-%d')))


    end_time = time.time()

    print(f"Runtime: {end_time - start_time} seconds.")