import os
import json
import re
import pandas as pd

def parse_filename(filename):
    match = re.match(r'rates_(.*?)_(.*?)\.json', filename)
    if match:
        brand_name, model_name = match.groups()
        return brand_name, model_name
    return None, None

def main():
    directory = '.'  # assuming the script is in the same folder as the JSON files
    combined_data = []
    excel_rows = []

    for filename in os.listdir(directory):
        if filename.startswith('rates_') and filename.endswith('.json'):
            brand_name, model_name = parse_filename(filename)
            if not brand_name or not model_name:
                continue

            with open(filename, 'r') as file:
                rates = json.load(file)

            issues = rates.get('issues')

            for issue in issues:
                issue_results = issue.get('results')
                issue_url = issue.get('url')
                issue_idx = issue.get('idx')
                issue_name = issue.get('name')

                for issue_result in issue_results:
                    data_row = {
                        'brand_name': brand_name,
                        'model_name': model_name,
                        'issue_idx': issue_idx,
                        'issue_name': issue_name,
                        'issue_url': issue_url,
                        **issue_result,
                    }
                    excel_rows.append(data_row)
            combined_data.append(rates)

    with open('combined_rates.json', 'w') as outfile:
        json.dump(combined_data, outfile, indent=4)

    with open('combined_excel_json_rates.json', 'w') as outfile_excel_json:
        json.dump(excel_rows, outfile_excel_json, indent=4)

    # Create Excel file with separate tabs for each brand
    if excel_rows:
        df = pd.DataFrame(excel_rows)
        with pd.ExcelWriter('combined_rates_by_brand.xlsx') as writer:
            for brand_name, group in df.groupby('brand_name'):
                group.to_excel(writer, sheet_name=brand_name, index=False)

if __name__ == '__main__':
    main()
