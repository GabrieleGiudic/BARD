import pickle 
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import urllib
import urllib.request
import urllib.parse
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
        list: A list of MP4 URLs.
    """

    driver = webdriver.Chrome()  # Replace with your preferred WebDriver
    driver.get(url)

    # Wait for the page to load
    
    wait = WebDriverWait(driver, 10)
    
    wait.until(EC.presence_of_element_located((By.TAG_NAME, 'video')))
    
    visible_mp4_urls = [a.get_attribute('src') for a in driver.find_elements(By.TAG_NAME, 'video') if a.is_displayed() and a.get_attribute('src').endswith('.mp4')]
   
    # Combine visible and hidden MP4 URLs
    all_mp4_urls = visible_mp4_urls

    driver.quit()
    return all_mp4_urls


main_folder = "../data"


for folder in os.listdir(main_folder):
    print(folder)
    subfolder_path = os.path.join(main_folder, folder)
    if os.path.isdir(subfolder_path):
        
        failed_file_path = os.path.join(subfolder_path, "failed.pkl")
        if os.path.exists(failed_file_path):
            with open(failed_file_path, "rb") as f:
                failed_data = pickle.load(f)
            url_info_path = os.path.join(subfolder_path, "url_info.pkl")
            with open(url_info_path, "rb") as f:
                url_info = pickle.load(f)
                    
            info_path = os.path.join(subfolder_path, "info.pkl")
            with open(info_path, "rb") as f:
                titles = pickle.load(f)
                    

                failed = {}
                for k in failed_data.keys():
                    print(k)
                    try: 
                        url = failed_data[k]
                        specific_url = failed_data[k]["url"]
                        mp4_urls = extract_mp4_urls(specific_url)
                        
                        mp4_urls = mp4_urls[0]
                        
                        urllib.request.urlretrieve(mp4_urls, os.path.join(main_folder,folder,str(k) + '.mp4'))
                        titles[int(k)] = "Time: " + url["time"] + ", Points: " + url['pts'] + ", Home: " + url['home'] + ", Desc: " + url['info']
                        print("done")
                    except:
                        print("failed")
                        failed[k] = url
                    
                
                with open(os.path.join(main_folder,folder,'info.pkl'), 'wb') as f:
                    pickle.dump(titles, f)
                
                
                with open(os.path.join(main_folder,folder,'failed.pkl'), 'wb') as f:
                    pickle.dump(failed, f)
            
        else:
            print("  -> failed.pkl not found")