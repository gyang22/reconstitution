import numpy as np
import yfinance as yf
from scipy.stats import lognorm
import matplotlib.pyplot as plt
import pandas as pd



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

stock_data = pd.read_csv("filtered_companies.csv")

baseline = stock_data.iloc[3000]['marketCap']

include = []
exclude = []

for i in range(2900, 3100):
    company = stock_data.iloc[i]['symbol']
    current_price = stock_data.iloc[i]['marketCap']
    dist = walk(current_price, 100, 0, 0.1)
    include.append((company, exceed_above_p(dist, baseline)))
    exclude.append((company, decrease_below_p(dist, baseline)))

print(include)
print(exclude)



