import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests
import numpy as np
import os

def extract_url_information(url):
    """Extracts URL information from a webpage using Selenium.

    Args:
        url (str): The URL of the webpage to extract information from.

    Returns:
        list: A list of dictionaries containing URL information.
    """

    driver = webdriver.Chrome()  # Replace with your preferred WebDriver
    driver.get(url)

    # Wait for the page to load
    random_seconds = np.random.randint(0, 2)
    wait = WebDriverWait(driver, random_seconds)
    wait.until(EC.presence_of_element_located((By.TAG_NAME, 'body')))

    wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'GamePlayByPlayRow_row__2iX_w')))
    play_rows = driver.find_elements(By.CLASS_NAME, "GamePlayByPlayRow_row__2iX_w")
    
    url_info = []
    pts = "0-0"
    for row in play_rows:
        # Extract text
        try:
            desc = row.text.split("\n")
            info = ""
            time = desc[0]
            if (len(desc)>2):
                pts = desc[1]
                info = desc[2]
            else:
                info = desc[1]
                
            
            # Attempt to find any link within the row
            link = row.find_element(By.TAG_NAME, "a")  # Adjust if the link tag is different
            url = link.get_attribute("href") if link else "No link found"
            
            # Print the results
            is_home_team = row.get_attribute("data-is-home-team")
            
            url_info.append({
                'url': url,
                'time': time,
                'pts':pts,
                'home': is_home_team,
                'info': info
            })
            
        except:
            continue
    
    driver.quit()
    return url_info

def extract_mp4_urls(url):
    """Extracts MP4 URLs from a webpage using Selenium.

    Args:
        url (str): The URL of the webpage to extract information from.

    Returns:
        tuple: A list of MP4 URLs, cookies, and user agent.
    """
    driver = webdriver.Chrome()  # Replace with your preferred WebDriver
    driver.get(url)

    # Wait for the page to load
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.TAG_NAME, 'video')))
    
    visible_mp4_urls = [a.get_attribute('src') for a in driver.find_elements(By.TAG_NAME, 'video') if a.is_displayed() and a.get_attribute('src').endswith('.mp4')]

    # Combine visible and hidden MP4 URLs
    all_mp4_urls = visible_mp4_urls

    cookies = driver.get_cookies()
    user_agent = driver.execute_script("return navigator.userAgent;")

    driver.quit()
    return all_mp4_urls, cookies, user_agent
    
# Path to your CSV
csv_path = '../dataset/dataset.csv'

# Directory to save the downloaded files
output_dir = '../data'

os.makedirs(output_dir, exist_ok=True)

# Load CSV
df = pd.read_csv(csv_path, sep=';')

# Download each URL as an MP4
for counter, url in enumerate(df['urls'], start=1):
    try:
        filename = os.path.join(output_dir, f"{counter}.mp4")
        print(f"Downloading {url} -> {filename}")
        specific_url = url
        
        mp4_urls, cookies, user_agent = extract_mp4_urls(specific_url)
        
        if not mp4_urls:
            print(f"No video found for {url}")
            continue
            
        target_mp4 = mp4_urls[0]
        
        session = requests.Session()
        for cookie in cookies:
            session.cookies.set(cookie['name'], cookie['value'])
            
        headers = {
            "User-Agent": user_agent,
            "Referer": "https://www.nba.com/",
            "Accept": "*/*"
        }
        
        response = session.get(target_mp4, headers=headers, stream=True)
        if response.status_code == 200:
            with open(filename, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            print(f"Success: {filename}")
        else:
            print(f"Failed to download {url}: Server returned status {response.status_code}")
        
    except Exception as e:
        print(f"Failed to download {url}: {e}")