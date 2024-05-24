import pandas as pd
import yfinance as yf
import torch
from torch import nn 
import torch.nn.functional as F
from torch.utils.data import DataLoader, TensorDataset
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
import time
from datetime import datetime, timedelta





class LinearRegressionNet(nn.Module):

    def __init__(self, feature_size: int):
        super().__init__()
        self.input = nn.Linear(feature_size, 64)
        self.linear = nn.Linear(64, 64)
        self.output = nn.Linear(64, 1)


    def forward(self, x):
        l = F.relu(self.input(x))
        l = F.relu(self.linear(l))
        l = F.relu(self.linear(l))
        return F.relu(self.output(l))


VUG_companies = pd.read_csv("data/VUG_constituents.csv")

x = []

labels = []

earliest_date = datetime.strptime(VUG_companies.iloc[0]['EndTime'], '%Y-%m-%d') - timedelta(days=50)

end_date = datetime.strptime(VUG_companies.iloc[-1]['EndTime'], '%Y-%m-%d') - timedelta(days=50)

for symbol in VUG_companies['Symbol'].unique():
    ticker = symbol.split(" ")[0]
    try:
        stock_info = yf.download(ticker, start=earliest_date.strftime('%Y-%m-%d'), end=end_date.strftime('%Y-%m-%d'))
    except Exception as e:
        print(f"No data for {ticker}. Ticker may be delisted.")
        continue

    for index, row in VUG_companies[VUG_companies['Symbol'] == symbol].iterrows():

        data_date = pd.to_datetime(row['EndTime'])
        
        if data_date not in stock_info.index:
            continue

        features = []

        # record the resulting weight
        labels.append(row['Weight'])

        # include present close and volume
        features.append(stock_info.loc[data_date]['Adj Close'])
        features.append(stock_info.loc[data_date]['Volume'])
        
        # include 30 day volatility
        past_date = data_date - timedelta(days=30)

        volatility_df = stock_info.loc[past_date:data_date].copy()
        volatility_df['Returns'] = volatility_df['Adj Close'].pct_change()
        volatility = volatility_df['Returns'].std()
        features.append(volatility)

        x.append(features)



print(len(x))
print(len(labels))


# Convert data to tensors
x_tensor = torch.tensor(x, dtype=torch.float32)
labels_tensor = torch.tensor(labels, dtype=torch.float32).view(-1, 1)

# Normalize the features
x_mean = x_tensor.mean(dim=0, keepdim=True)
x_std = x_tensor.std(dim=0, keepdim=True)
x_tensor = (x_tensor - x_mean) / (x_std + 1e-8)

# Split the dataset into training and testing sets
x_train, x_test, y_train, y_test = train_test_split(x_tensor, labels_tensor, test_size=0.2, random_state=42)

# Create DataLoaders
train_dataset = TensorDataset(x_train, y_train)
test_dataset = TensorDataset(x_test, y_test)
train_loader = DataLoader(train_dataset, batch_size=2, shuffle=True)
test_loader = DataLoader(test_dataset, batch_size=2, shuffle=False)


model = LinearRegressionNet(feature_size=x_tensor.shape[1])
loss_func = nn.MSELoss()
optimizer = torch.optim.Adam(model.parameters(), lr=1e-4)

num_epochs = 100
for epoch in range(num_epochs):
    model.train()
    for batch_x, batch_labels in train_loader:
        optimizer.zero_grad()  # Zero the gradients
        outputs = model(batch_x)  # Forward pass
        loss = loss_func(outputs, batch_labels)  # Compute the loss
        if torch.isnan(loss):
            print("Loss is NaN. Exiting...")
            break
        loss.backward()  # Backpropagate the error
        optimizer.step()  # Update the model parameters

    if torch.isnan(loss):
        break
    print(f'Epoch {epoch+1}/{num_epochs}, Loss: {loss.item()}')


torch.save(model.state_dict(), 'linear_regression_model.pth')
print("Model saved.")


model.eval()
all_preds = []
all_labels = []
with torch.no_grad():
    for batch_x, batch_labels in test_loader:
        outputs = model(batch_x)
        all_preds.extend(outputs.numpy().flatten())
        all_labels.extend(batch_labels.numpy().flatten())

mse = mean_squared_error(all_labels, all_preds)
print(f'Test Mean Squared Error: {mse:.4f}')

