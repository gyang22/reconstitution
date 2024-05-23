import re

def rtf_to_csv(rtf_file_path, csv_file_path):
    with open(rtf_file_path, 'r') as rtf_file:
        rtf_content = rtf_file.read()

    # Extract the CSV content from the RTF format
    csv_content = re.sub(r'\\[a-zA-Z]+\d*', '', rtf_content)  # Remove RTF control words
    csv_content = re.sub(r'[{}]', '', csv_content)  # Remove braces
    csv_content = re.sub(r'\\$', '', csv_content, flags=re.MULTILINE)  # Remove trailing backslashes
    csv_content = csv_content.strip()

    # Write to CSV file
    with open(csv_file_path, 'w') as csv_file:
        csv_file.write(csv_content)

# Example usage
rtf_file_path = 'SPY_constituents.rtf'
csv_file_path = 'SPY_constituents.csv'
rtf_to_csv(rtf_file_path, csv_file_path)
