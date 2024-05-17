import pandas as pd
import yfinance as yf


company_df = pd.read_csv("top_companies.csv")


'''
Condition 1: "All companies that are determined to be part of the US equity market are included in the Russell US indexes."
"All securities eligible for inclusion in Russell US indexes must trade on an eligible US exchange. Bulletin board, pink sheet 
or over-the-counter (OTC) traded securities are not eligible for inclusion, including securities for which prices are displayed 
on the FINRA ADF."
"Eligible US exchanges: CBOE, NYSE, NYSE American, NASDAQ, ARCA."
'''

eligible_exchanges = ["NYSE", "NASDAQ", "AMEX", "ARCA", "CBOE"]

company_df = company_df[company_df['exchange'].isin(eligible_exchanges)]


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


'''
Condition 3: "Companies with a total market capitalisation less than $30 million are not eligible for inclusion in Russell 
US indexes."
'''

company_df = company_df[company_df['marketCap'] >= 30e6]