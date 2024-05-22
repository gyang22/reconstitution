import requests
import xml.etree.ElementTree as ET
import time



headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}




def fetch_filing_index(cik, start_date, end_date):
    base_url = "https://www.sec.gov/cgi-bin/browse-edgar"
    params = {
        'action': 'getCompany',
        'CIK': cik,
        'type': 'NPORT',
        'dateb': end_date,
        'datea': start_date,
        'owner': 'exclude',
        'output': 'atom',
        'count': '100'
    }

    retries = 5
    for i in range(retries):
        response = requests.get(base_url, headers=headers, params=params)
        if response.status_code == 200:
            return response.content
        elif response.status_code == 503:
            print(f"503 Service Unavailable. Retrying in {2 ** i} seconds...")
            time.sleep(2 ** i)
        else:
            print(f"Failed to fetch filing index: {response.status_code}")
            return None
    return None
    
def parse_filing_index(index_content):
    root = ET.fromstring(index_content)
    ns = {'atom': 'http://www.w3.org/2005/Atom'}
    entries = root.findall('atom:entry', ns)
    links = [entry.find('atom:link', ns).get('href') for entry in entries]
    return links

def fetch_and_parse_filings(filing_links):
    for link in filing_links:
        retries = 5
        for i in range(retries):
            response = requests.get(link, headers=headers)
            if response.status_code == 200:
                root = ET.fromstring(response.content)
                # Extract relevant data from the XML tree
                # Adjust based on the XML structure
                for holding in root.findall('.//ns:holding', {'ns': 'http://www.sec.gov/edgar/document/thirteenf/informationtable'}):
                    name = holding.find('ns:nameOfIssuer', {'ns': 'http://www.sec.gov/edgar/document/thirteenf/informationtable'}).text
                    cusip = holding.find('ns:cusip', {'ns': 'http://www.sec.gov/edgar/document/thirteenf/informationtable'}).text
                    value = holding.find('ns:value', {'ns': 'http://www.sec.gov/edgar/document/thirteenf/informationtable'}).text
                    print(f"Name: {name}, CUSIP: {cusip}, Value: {value}")
                break
            elif response.status_code == 503:
                print(f"503 Service Unavailable. Retrying in {2 ** i} seconds...")
                time.sleep(2 ** i)
            else:
                print(f"Failed to fetch filing document: {response.status_code}")
                break
        # Add delay to avoid rate limiting
        time.sleep(1)

cik = '0000884394' # SPY
start_date = '2023-01-01'
end_date = '2023-12-31'
index_content = fetch_filing_index(cik, start_date, end_date)
if index_content:
    filing_links = parse_filing_index(index_content)
    fetch_and_parse_filings(filing_links)