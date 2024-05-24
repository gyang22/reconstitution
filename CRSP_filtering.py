import pandas as pd

company_df = pd.read_csv("data/top_companies.csv")

print(f'Number of companies: {len(company_df)}')

us_territories = ['United States', 'Puerto Rico', 'Guam', 'American Samoa', 'U.S. Virgin Islands', 'Northern Mariana Islands']
doc = ['Bermuda', 'Cayman Islands', 'British Virgin Islands']
th = ['Switzerland', 'Ireland', 'Luxembourg', 'Netherlands']

company_df = company_df[(company_df['country'] == "United States") | (company_df['country'].isin(us_territories + doc + th))]

print(f'Number of companies after country HQ condition: {len(company_df)}')



company_df = company_df[company_df['marketCap'] >= 15e6]

company_df['floatPercentage'] = (company_df['floatShares'] / company_df['sharesOutstanding']) * 100

company_df = company_df[company_df['floatPercentage'] >= 12.5]

print(f'Number of companies after market cap and float condition: {len(company_df)}')



company_df.to_csv("data/CRSP_filtered_companies.csv")


