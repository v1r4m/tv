from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import json
import re

def extract_twitter_tokens():
    # Set Chrome options
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # Run in headless mode
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})  # Enable performance logging
    
    # Initialize WebDriver
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    try:
        # Open Twitter login page
        print("Opening Twitter login page...")
        driver.get('https://twitter.com/i/flow/login')
        time.sleep(3)
        
        # User input
        username = input("Twitter username: ")
        password = input("Twitter password: ")
        
        # Enter username
        username_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[autocomplete='username']"))
        )
        username_input.send_keys(username)
        username_input.send_keys(Keys.RETURN)
        time.sleep(2)
        
        # Enter password
        password_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='password']"))
        )
        password_input.send_keys(password)
        password_input.send_keys(Keys.RETURN)
        time.sleep(5)
        
        # Extract cookies and token info
        cookies = driver.get_cookies()
        auth_token = None
        ct0 = None
        guest_token = None
        authorization = None
        
        # Get authorization token from network requests
        logs = driver.get_log('performance')
        for log in logs:
            if 'Network.requestWillBeSent' in str(log):
                try:
                    request = json.loads(log['message'])['message']['request']
                    if 'authorization' in request['headers']:
                        authorization = request['headers']['authorization']
                        break
                except:
                    continue
        
        for cookie in cookies:
            if cookie['name'] == 'auth_token':
                auth_token = cookie['value']
            elif cookie['name'] == 'ct0':
                ct0 = cookie['value']
            elif cookie['name'] == 'gt':
                guest_token = cookie['value']
        
        # Print results
        print("\n=== Extracted Token Info ===")
        print(f"auth_token: {auth_token}")
        print(f"ct0: {ct0}")
        print(f"guest_token: {guest_token}")
        print(f"authorization: {authorization}")
        
        # Save token info to file
        token_data = {
            'auth_token': auth_token,
            'ct0': ct0,
            'guest_token': guest_token,
            'authorization': authorization,
            'cookies': cookies
        }
        
        with open('twitter_tokens.json', 'w') as f:
            json.dump(token_data, f, indent=2)
        
        print("\nToken info saved to twitter_tokens.json.")
        
        # Example API request
        print("\n=== Example API Request ===")
        print("curl 'https://x.com/i/api/2/badge_count/badge_count.json?supports_ntab_urt=1' \\")
        print(f"  -H 'authorization: {authorization}' \\")
        print(f"  -b 'auth_token={auth_token}; ct0={ct0}; gt={guest_token}' \\")
        print(f"  -H 'x-csrf-token: {ct0}'")
        
    except Exception as e:
        print(f"Error: {str(e)}")
    
    finally:
        driver.quit()

if __name__ == "__main__":
    extract_twitter_tokens() 