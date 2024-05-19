import pandas as pd
import yfinance as yf
import torch
from torch import nn 


filtered_companies = pd.read_csv("filtered_companies.csv", low_memory=False)

'''
Gather historical index data.
'''

class Russell1000(nn.Module):
    
    def __init__(self, num_features):
        super().__init__()

        self.flatten = nn.Flatten()
        self.hidden = nn.Sequential(
            nn.Linear(num_features, 128),
            nn.ReLU(),
            nn.Linear(128, 128),
            nn.ReLU(),
            nn.Linear(128, 128),
            nn.Sigmoid(),
            nn.Linear(128, 1)
        )

    def forward(self, x):
        x = self.flatten(x)
        x = self.hidden(x)

        return x



