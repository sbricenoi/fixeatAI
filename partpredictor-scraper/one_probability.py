import time
from seleniumbase import Driver
from selenium.webdriver.common.by import By
import json

def one_probability_scrape(brands=[]):
    driver = Driver(uc=True)
    issues_filename = 'combined_issues.json'
    with open(issues_filename, 'r') as file:
        issues_general_list = json.load(file)

    for idx, brand_obj in enumerate(issues_general_list):
        brand_name = brand_obj['brand']
        brand_idx = brand_obj['idx']
        if idx not in brands:
            continue

        print(f"[{brand_idx}]BRAND ANALIZING {brand_name}")
        models = brand_obj['models']
        for idx, model_obj in enumerate(models):
            issues_error_list = []
            issues_results = []
            model_name = model_obj['model']
            model_idx = model_obj['idx']
            print(f"*** [{model_idx}] MODEL ANALIZING {model_name}")

            issues = model_obj['issues']

            for idx, issue_obj in enumerate(issues):
                # Initialize an empty list to store the results
                results = []
                issue_name = issue_obj['name']
                issue_idx = issue_obj['idx']
                issue_url = issue_obj['url']

                print(f"****** [{issue_idx}] ISSUE ANALIZING {issue_name}")

                try:
                    driver.uc_open_with_reconnect(issue_url, 3)
                    time.sleep(2)

                    # Open a new tab
                    driver.execute_script("window.open('');")
                    # Switch to the new tab
                    driver.switch_to.window(driver.window_handles[1])
                    print("Switched to the new tab.")

                    # Load the same URL in the new tab
                    driver.get(issue_url)
                    driver.close()
                    print("Original tab closed.")
                    # Close the original tab
                    time.sleep(1)
                    driver.switch_to.window(driver.window_handles[0])
                    time.sleep(1)

                    # Switch back to the new tab
                    driver.switch_to.window(driver.window_handles[0])
                    print("Switched to the new tab.")
                    time.sleep(5)
                    print("GETTING DIV ELEMENTS")

                    # Check if no results
                    try:
                        # Try to find the h2 element with the class 'no-search__headline'
                        h2_not_found = driver.find_element(By.CLASS_NAME, "no-search__headline")
                        if h2_not_found:
                            raise Exception("NOT FOUND")
                    except Exception:
                        print("RESULTS FOUND")

                    # Find all the target div elements
                    div_elements = driver.find_elements(By.CLASS_NAME, "part-predictor-product__item-wrapper")

                    print("DIV ELEMENTS", div_elements, len(div_elements))

                    # Iterate over each div element and extract the required information
                    for div in div_elements:
                        item = {}
                        
                        # Get the image src
                        img_element = div.find_element(By.CLASS_NAME, "js-product-img")
                        item["image_src"] = img_element.get_attribute("src")

                        print(f"IMAGE SRC {item['image_src']}")
                        
                        # Get the product name
                        name_element = div.find_element(By.CLASS_NAME, "part-predictor-product__item-name").find_element(By.TAG_NAME, "a")
                        item["product_name"] = name_element.text
                        print(f"PRODUCT NAME {item['product_name']}")
                        
                        # Get the manufacturer info
                        mnf_element = div.find_element(By.CLASS_NAME, "part-predictor-product__info-item.info__item-mnf")
                        item["manufacturer_info"] = mnf_element.text
                        print(f"MANUFACTURER INFO {item['manufacturer_info']}")
                        
                        # Get the general info items
                        info_items = div.find_elements(By.CLASS_NAME, "part-predictor-product__info-item")
                        item["info_item_1"] = info_items[0].text if len(info_items) > 0 else ""
                        item["info_item_2"] = info_items[1].text if len(info_items) > 1 else ""
                        item["info_item_3"] = info_items[2].text if len(info_items) > 2 else ""
                        
                        # Get the fix rate and cast to float
                        fix_rate_element = div.find_element(By.CLASS_NAME, "part-predictor-product__fix-rate-inner")
                        item["fix_rate"] = float(fix_rate_element.text.replace("%", "").replace(",", "").replace(" ", "").replace("\n", ""))
                        
                        # Get the product list price
                        try:
                        
                            price_element = div.find_element(By.CLASS_NAME, "js-product-listPrice.visible")
                            item["list_price"] = price_element.text
                        except Exception:
                            print("PRICE NOT AVAILABLE")

                        print("ITEM", item)
                        
                        # Add the item to the results list
                        results.append(item)

                except Exception as e:
                    print(e)
                    issue_error = {
                        'brand': brand_name,
                        'brand_idx': brand_idx,
                        'model': model_name,
                        'model_idx': model_idx,
                        'issue': issue_name,
                        'issue_idx': issue_idx,
                        'issue_url': issue_url,
                        'error': str(e)
                    }
                    issues_error_list.append(issue_error)

                issues_results.append({
                    'name': issue_name,
                    'idx': issue_idx,
                    'url': issue_url,
                    'results': results
                })
            
            # Save issues results
            with open(f'rates_{brand_name}_{model_name}.json', 'w') as f:
                brand_model_issue_rates = {
                    'brand': brand_name,
                    'model': model_name,
                    'issues': issues_results
                }
                json.dump(brand_model_issue_rates, f, indent=4)
    
            # Save Issue errors to a file with timestamp in its name
            if len(issues_error_list) > 0:
                with open(f'issues_errors_{brand_name}_{model_name}_{time.time()}.json', 'w') as f:
                    json.dump(issues_error_list, f, indent=4)


def get_counter():
    issues_filename = 'combined_issues.json'
    counter = 0
    with open(issues_filename, 'r') as file:
        issues_general_list = json.load(file)

    for idx, brand_obj in enumerate(issues_general_list):
        models = brand_obj['models']
        for idx, model_obj in enumerate(models):
            issues = model_obj['issues']

            len_issues = len(issues)
            counter += len_issues
    print("COUNTER", counter)
    return counter

if __name__ == "__main__":
    brands = []
    model_index = -1
    brand_index_input = input("Brands IDX (separated by comma):")
    if (brand_index_input != ''):
        brands = brand_index_input.split(',')
        brands = [int(brand) for brand in brands]
    model_index_input = input("Model IDX:")
    if (model_index_input != ''):
        model_index = int(model_index_input)
    print(f"---> BRANDS {brands}")
    print(f"---> MODEL {model_index}")
    one_probability_scrape(brands=brands)

# if __name__ == "__main__":
#     get_counter()