import pandas as pd
import yfinance as yf


company_df = pd.read_csv("top_companies.csv")

print(f'Number of companies: {len(company_df)}')

'''
Condition 1: "All companies that are determined to be part of the US equity market are included in the Russell US indexes."
"All securities eligible for inclusion in Russell US indexes must trade on an eligible US exchange. Bulletin board, pink sheet 
or over-the-counter (OTC) traded securities are not eligible for inclusion, including securities for which prices are displayed 
on the FINRA ADF."
"Eligible US exchanges: CBOE, NYSE, NYSE American, NASDAQ, ARCA."
'''

eligible_exchanges = set(["NYSE", "NASDAQ", "AMEX", "ARCA", "CBOE"]) # for some reason the format in the data is different?

#company_df = company_df[company_df['exchange'].isin(eligible_exchanges)]

print(f'Updated number of companies after condition 1: {len(company_df)}')


'''
Condition 2: "A stock must have a close price at or above $1.00 (on its primary exchange) on rank day to be considered 
eligible for inclusion. In order to reduce unnecessary turnover, if an existing index member's closing price is less than $1.00 
on rank day, it will be considered eligible if the average of the daily closing prices (from its primary exchange) during the 
30 days prior to the rank date is equal to or greater than $1.00. If an existing index member does not trade on the rank day, 
it must price at $1.00 or above on another eligible US exchange to remain eligible. A stock added during the quarterly IPOs 
process is considered a new index addition and therefore must have a close price on its primary exchange at or above $1.00 on 
the last day of the IPO eligibility period in order to qualify for index inclusion."
'''

company_df = company_df[company_df['previousClose'] > 1.0]

print(f'Updated number of companies after condition 2: {len(company_df)}')


'''
Condition 3: "Companies with a total market capitalisation less than $30 million are not eligible for inclusion in Russell 
US indexes."
'''

company_df = company_df[company_df['marketCap'] >= 30e6]

print(f'Updated number of companies after condition 3: {len(company_df)}')


'''
Condition 4: "Companies with less than an absolute 5% of shares available will be removed from eligibility."
Use the formula (floatShares / sharesOutstanding) * 100 to find available share percentage.
'''

company_df['floatPercentage'] = (company_df['floatShares'] / company_df['sharesOutstanding']) * 100

company_df = company_df[company_df['floatPercentage'] >= 5]

print(f'Updated number of companies after condition 4: {len(company_df)}')


'''
Condition 5: "Companies structured in the following ways are excluded from inclusion in Russell indexes: royalty trusts, US 
limited liability companies, closed-end investment companies (as a point of clarification: companies that are required to 
report acquired fund fees and expenses as defined by the SEC, including business development companies, are not eligible for 
inclusion), blank-cheque companies, special-purpose acquisition companies (SPACs), and limited partnerships. Exchange traded 
funds (ETFs) and mutual funds are also excluded."
'''

# find out how to do this


'''
Condition 6: UBTI Screening
'''

# also clarify this


'''
Condition 7: "The following share types are not eligible for inclusion: preferred and convertible preferred stock, redeemable 
shares, participating preferred stock, warrants, rights, depositary receipts, installment receipts and trust receipts."
'''


'''
Condition 8: "Stocks must be listed on the rank day and FTSE Russell must have access to documentation on that date supporting 
the company's eligibility for index inclusion. This includes corporate description, verification of incorporation, number of 
shares outstanding and other information needed to determine eligibility. IPOs will be considered for index inclusion on a 
quarterly basis."
'''


'''
Condition 9: "Companies assigned a developed market nationality are required to have 5% or greater of the company's voting 
rights (aggregated across all of its equity securities, including, where identifiable, those that are not listed or trading) 
in the hands of unrestricted shareholders or they will be deemed ineligible for index inclusion. Shares referenced as non-voting 
or provide legally minimum rights only will be viewed as having no voting power as it relates to the minimum voting rights 
review. Emerging market securities are not subject to this requirement."
'''

emerging_markets = set(["Brazil", "Chile", "Colombia", "Mexico", "Peru",
                    "Czech Republic", "Egypt", "Greece", "Hungary", "Kuwait", "Poland", "Qatar", "Saudi Arabia", "South Africa",
                    "Turkey", "United Arab Emirates",
                    "China", "India", "Indonesia", "Korea", "Malaysia", "Philippines", "Taiwan", "Thailand"])

#company_df = company_df[company_df['country'].isin(emerging_markets)] # need to find voting rights info


company_df.to_csv("filtered_companies.csv")