import numpy as np
import yfinance as yf
from scipy.stats import lognorm
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime, timedelta



"""
From a starting value, perform a random walk with log normal distribution movement factor.
Returns the interval of possible values and the corresponding distribution over the interval.
"""
def walk(start: float, time_elapsed: int, mean: float, var: float):
    start_mean = np.log(start) + time_elapsed * mean
    log_var = np.sqrt(time_elapsed) * var

    dist = lognorm(s=log_var, scale=np.exp(start_mean))

    return dist


def show_values(start, time_elapsed, mean, var):
    distribution = walk(start, time_elapsed, mean, var)

    x = np.linspace(distribution.ppf(0.01), distribution.ppf(0.99), 1000)

    plt.figure(figsize=(10, 6))
    plt.plot(x, distribution.pdf(x), 'r-', lw=2, label='Log-normal PDF')
    plt.title('Distribution of Final Values')
    plt.xlabel('Final Value')
    plt.ylabel('Probability Density')
    plt.legend()
    plt.show()

#show_values(1500, 10, 0, 0.1)

"""
Given a distribution and a target, returns the probability of dipping below the target.
"""
def decrease_below_p(distribution: lognorm, target: float):
    return distribution.cdf(target)

"""
Given a distribution and a target, returns the probability of exceeding the target.
"""
def exceed_above_p(distribution: lognorm, target: float):
    return 1 - distribution.cdf(target)


# dist = walk(1500, 10, 0, 0.1)

# print(decrease_below_p(distribution=dist, target=1300))
# print(exceed_above_p(distribution=dist, target=1600))

stock_data = pd.read_csv("filtered_companies.csv", low_memory=False)

stock_data = stock_data.sort_values('marketCap', ascending=False)

baseline = stock_data.iloc[3000]['marketCap']

include = []
exclude = []

for i in range(2970, 3030):
    company = stock_data.iloc[i]['symbol']
    current_cap = stock_data.iloc[i]['marketCap']
    shares_outstanding = stock_data.iloc[i]['sharesOutstanding']
    
    end_date = datetime.today()
    start_date = end_date - timedelta(days=50)

    historical_data = yf.download(company, start=start_date.strftime('%Y-%m-%d'), end=end_date.strftime('%Y-%m-%d'))
    historical_data['marketCaps'] = historical_data['Adj Close'] * shares_outstanding

    historical_data['marketCapReturn'] = historical_data['marketCaps'].pct_change()

    market_cap_volatility = historical_data['marketCapReturn'].std()
    

    dist = walk(current_cap, 150, 0, market_cap_volatility**2)
    include.append((company, exceed_above_p(dist, baseline)))
    exclude.append((company, decrease_below_p(dist, baseline)))

print(include)
print(exclude)

tickers = [item[0] for item in include]
values = [item[1] for item in include]

def get_gradient_color(value, min_value, max_value, color1, color2):
    ratio = (value - min_value) / (max_value - min_value)
    color = plt.cm.RdYlGn(ratio)  # Use a colormap for the gradient (e.g., RdYlGn for red to green)
    return color

min_value = 0.0
max_value = 1.0
colors = []
for ticker, value in include:
    current_cap = stock_data.loc[stock_data['symbol'] == ticker, 'marketCap'].values[0]
    if current_cap >= baseline: # began above baseline and likely to stay
        colors.append(get_gradient_color(value, min_value, max_value, 'red', 'grey'))
    elif current_cap < baseline: # began below baseline and likely to join
        colors.append(get_gradient_color(value, min_value, max_value, 'grey', 'green'))


plt.figure(figsize=(15, 7))
plt.bar(tickers, values, color=colors)

plt.xlabel("Tickers")
plt.ylabel("Probability of being included")
plt.xticks(rotation=90)
plt.show()



