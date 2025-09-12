import time
from seleniumbase import Driver
from selenium.webdriver.common.by import By
import json

def oem_scrape(brand_starting_index=0, model_starting_index=0):

    driver = Driver(uc=True)
    url = "https://www.partstown.com/part-predictor"
    driver.uc_open_with_reconnect(url, 3)
    time.sleep(2)

    # Open a new tab
    driver.execute_script("window.open('');")
    # Switch to the new tab
    driver.switch_to.window(driver.window_handles[1])
    print("Switched to the new tab.")

    # Load the same URL in the new tab
    driver.get(url)
    driver.close()
    print("Original tab closed.")
    # Close the original tab
    time.sleep(1)
    driver.switch_to.window(driver.window_handles[0])
    time.sleep(1)

    # Switch back to the new tab
    driver.switch_to.window(driver.window_handles[0])
    print("Switched to the new tab.")
    time.sleep(1)
    print("CLICKING CLOSE BTN")

    # Locate the button using its class name
    button = driver.find_element(By.CLASS_NAME, "part-predictor-steps__select-button")
    
    # Click the button
    button.click()
    print("Selected Brand Button clicked successfully.")
    

    ul_element_item = driver.find_element(By.CLASS_NAME, "part-predictor-steps__select-list")
    li_element_items = ul_element_item.find_elements(By.TAG_NAME, "li")
    print("LI ELEMENTS", li_element_items)

    brand_items_list = []

    if ul_element_item:
        # Find all li elements inside the ul

        for item in li_element_items:
            print(item.text)
            brand_obj = {}
            brand_name = item.text
            brand_parsed_name = brand_name.replace(" ", "-").lower()
            brand_obj['name'] = brand_name
            brand_obj['parsed_name'] = brand_parsed_name

            brand_items_list.append(brand_obj)

        brands = [{"name": obj['name'], "parsed_name": obj['parsed_name']} for obj in brand_items_list]

        # Save the brands list to a JSON file
        with open('brands.json', 'w') as f:
            json.dump(brands, f, indent=4)

        print("Brands saved to brands.json")
        time.sleep(3)
        button.click()

        # Loop through each brand name and click on the corresponding li element
        for idx, brand in enumerate(brand_items_list):
            time.sleep(3)
            print(f"*** ANALIZING {idx} : {brand['name']}")
            if idx <= brand_starting_index:
                print("===== HARD PASSING BRAND")
                continue
            
            # Open the Brands list options by clickin gin button
            button = driver.find_element(By.CLASS_NAME, "part-predictor-steps__select-button")
            driver.execute_script("arguments[0].scrollIntoView(true);", button)
            # Click the button element using JavaScript to avoid interception
            driver.execute_script("arguments[0].click();", button)
    
            # Click the button
            #button.click()
            print("*** Selected Brand Button clicked successfully.")
            time.sleep(4)

            ul_element_item = driver.find_element(By.CLASS_NAME, "part-predictor-steps__select-list")
            li_element_items = ul_element_item.find_elements(By.TAG_NAME, "li")
            try:
                # Locate the li element by its text content
                li_element = li_element_items[idx]
                print("---> LI ELEMENT", li_element)
                driver.execute_script("arguments[0].scrollIntoView(true);", li_element)
                # Click the button element using JavaScript to avoid interception
                driver.execute_script("arguments[0].click();", li_element)
                # Click the li element
                #li_element.click()
                time.sleep(5)
                # Locate the button using its class name
                buttons = driver.find_elements(By.CLASS_NAME, "part-predictor-steps__select-button")
                model_button = buttons[1]
                # Click the button
                model_button.click()
                print("--- Model Button clicked successfully.")
                time.sleep(1)
                ul_element_items = driver.find_elements(By.CLASS_NAME, "part-predictor-steps__select-list")
                model_ul_element_item = ul_element_items[0]
                model_li_element_items = model_ul_element_item.find_elements(By.TAG_NAME, "li")
                print("---> MODEL LI ELEMENTS", model_li_element_items)

                model_items_list = []

                if model_ul_element_item:
                    # Find all li elements inside the ul

                    for item in model_li_element_items:
                        print(item.text)
                        model_obj = {}
                        model_name = item.text
                        model_parsed_name = model_name.replace(" ", "-").replace("/","-").lower()
                        model_obj['name'] = model_name
                        model_obj['parsed_name'] = model_parsed_name
                        model_items_list.append(model_obj)

                    models = [{"name": obj['name'], "parsed_name": obj['parsed_name']} for obj in model_items_list]

                    # Save the brands list to a JSON file
                    with open(f'models_{brand['parsed_name']}.json', 'w') as f:
                        json.dump(models, f, indent=4)

                    print(f"--> Models of {brand['name']} saved to models_{brand['parsed_name']}.json")
                    time.sleep(3)

                    # Reset the Model selector
                    model_button.click()

                    for model_idx, model in enumerate(model_items_list):
                        print(f"*********** ANALIZING {model_idx} : {model['name']}")
                        if idx <= model_starting_index:
                            print("========== HARD PASSING")
                            continue
                        search_box_elements = driver.find_elements(By.CLASS_NAME, "part-predictor-steps.js-part-predictor-steps")
                        search_box = search_box_elements[0]
                        driver.execute_script("arguments[0].scrollIntoView(true);", search_box)
                        # Click the button element using JavaScript to avoid interception
                        driver.execute_script("arguments[0].click();", search_box)

                        time.sleep(3)
                        buttons = driver.find_elements(By.CLASS_NAME, "part-predictor-steps__select-button")
                        model_button = buttons[1]
                        driver.execute_script("arguments[0].scrollIntoView(true);", model_button)
                        # Click the button element using JavaScript to avoid interception
                        driver.execute_script("arguments[0].click();", model_button)
                        time.sleep(1)
                        # Click the button
                        # model_button.click()
                        print("********** Selected Model Button clicked successfully.")
                        time.sleep(4)

                        model_ul_element_item = driver.find_element(By.CLASS_NAME, "part-predictor-steps__select-list")
                        model_li_element_items = model_ul_element_item.find_elements(By.TAG_NAME, "li")
                        try:
                            # Locate the li element by its text content
                            model_li_element = model_li_element_items[model_idx]
                            print("----------> MODEL LI ELEMENT", model_li_element)
                            # Scroll the button element into view using JavaScript
                            driver.execute_script("arguments[0].scrollIntoView(true);", model_li_element)
                            # Click the button element using JavaScript to avoid interception
                            driver.execute_script("arguments[0].click();", model_li_element)
                            # Click the li element
                            # model_li_element.click()
                            time.sleep(5)
                            print("SCROLL INTO BOX")
                            search_box_elements = driver.find_elements(By.CLASS_NAME, "part-predictor-steps.js-part-predictor-steps")
                            search_box = search_box_elements[0]
                            driver.execute_script("arguments[0].scrollIntoView(true);", search_box)
                            # Click the button element using JavaScript to avoid interception
                            driver.execute_script("arguments[0].click();", search_box)
                            time.sleep(2)
                            # Locate the button using its class name
                            buttons = driver.find_elements(By.CLASS_NAME, "part-predictor-steps__select-button")
                            issue_button = buttons[2]
                            # Click the button
                            issue_button.click()
                            print("--------- Issue Button clicked successfully.")
                            time.sleep(1)
                            issue_ul_element_items = driver.find_elements(By.CLASS_NAME, "part-predictor-steps__select-list")
                            issue_ul_element_item = issue_ul_element_items[0]
                            issue_li_element_items = issue_ul_element_item.find_elements(By.TAG_NAME, "li")
                            print("-----------> ISSUE LI ELEMENTS", issue_li_element_items)

                            issue_items_list = []

                            if issue_ul_element_items:
                                # Find all li elements inside the ul

                                for item in issue_li_element_items:
                                    print(item.text)
                                    issue_obj = {}
                                    issue_name = item.text
                                    issue_parsed_name = issue_name.replace(" ", "-").replace("/","-").lower()
                                    issue_obj['name'] = issue_name
                                    issue_obj['parsed_name'] = issue_parsed_name

                                    issue_items_list.append(issue_obj)

                                issues = [{"name": obj['name'], "parsed_name": obj['parsed_name']} for obj in issue_items_list]

                                # Save the brands list to a JSON file
                                with open(f'issues_{brand['parsed_name']}_{model['parsed_name']}.json', 'w') as f:
                                    json.dump(issues, f, indent=4)

                                print(f"---------> Issues of model {model['name']} of {brand['name']} saved to issues_{brand['parsed_name']}_{model['parsed_name']}.json")
                        except Exception as e:
                            print(f"Could not click on {model}: {e}")
            except Exception as e:
                print(f"Could not click on {brand}: {e}")
    else:
        print("ul element with the specified class not found")




if __name__ == "__main__":
    brand_starting_index = 0
    model_starting_index = 0
    brand_starting_index_input = input("Brand IDX:")
    if (brand_starting_index_input != ''):
        brand_starting_index = int(brand_starting_index_input)
    model_starting_index_input = input("Model IDX:")
    if (model_starting_index_input != ''):
        model_starting_index = int(model_starting_index_input)
    oem_scrape(brand_starting_index=brand_starting_index, model_starting_index=model_starting_index)