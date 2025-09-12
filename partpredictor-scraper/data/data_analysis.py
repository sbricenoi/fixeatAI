import os
import json
import re

def parse_filename(filename):
    match = re.match(r'issues_(.*?)_(.*?)\.json', filename)
    if match:
        brand_name, model_name = match.groups()
        return brand_name, model_name
    return None, None

def main():
    directory = '.'  # assuming the script is in the same folder as the JSON files
    combined_data = []
    brand_dict = {}

    for filename in os.listdir(directory):
        if filename.startswith('issues_') and filename.endswith('.json'):
            brand_name, model_name = parse_filename(filename)
            parsed_brand_name = brand_name.lower().replace(' ', '-').replace('/', '-').replace('+','')
            parsed_model_name = model_name.lower().replace(' ', '-').replace('/', '-').replace('+','').replace(".", "-")
            if not brand_name or not model_name:
                continue

            with open(filename, 'r') as file:
                issues = json.load(file)

            if brand_name not in brand_dict:
                brand_dict[brand_name] = {'idx': len(brand_dict), 'brand': brand_name, 'models': []}

            model_dict = {
                'idx': len(brand_dict[brand_name]['models']),
                'model': model_name,
                'issues': []
            }

            for issue_idx, issue in enumerate(issues):
                parsed_issue_name = issue['name'].lower().replace(' ', '-').replace('/', '-').replace("'", "").replace('+','').replace(".", "-")
                model_dict['issues'].append({
                    'idx': issue_idx,
                    'name': issue['name'],
                    'url': f'https://www.partstown.com/part-predictor/{parsed_brand_name}/{parsed_model_name}/{parsed_issue_name}'
                })

            brand_dict[brand_name]['models'].append(model_dict)

    combined_data = list(brand_dict.values())

    with open('combined_issues.json', 'w') as outfile:
        json.dump(combined_data, outfile, indent=4)

if __name__ == '__main__':
    main()