import pickle 
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import urllib
import urllib.request
import urllib.parse
import time
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


addresses_list = [
"/game/dal-vs-gsw-0022401228/play-by-play",
"/game/por-vs-phx-0022401219/play-by-play",
"/game/bos-vs-was-0022401217/play-by-play",
"/game/min-vs-sas-0022401218/play-by-play",
"/game/nyk-vs-orl-0022401227/play-by-play",
"/game/nop-vs-ind-0022401216/play-by-play",
"/game/mem-vs-lal-0022401220/play-by-play",
"/game/mia-vs-det-0022401221/play-by-play",
"/game/uta-vs-lac-0022401226/play-by-play",
"/game/chi-vs-tor-0022401223/play-by-play",
"/game/phi-vs-cha-0022401222/play-by-play",
"/game/den-vs-sac-0022401225/play-by-play",
"/game/cle-vs-bkn-0022401224/play-by-play",
"/game/mil-vs-okc-0062400001/play-by-play",
"/game/gsw-vs-mem-0022400366/play-by-play",
"/game/nyk-vs-min-0022400367/play-by-play",
"/game/den-vs-por-0022400371/play-by-play",
"/game/nop-vs-hou-0022400365/play-by-play",
"/game/lac-vs-dal-0022400368/play-by-play",
"/game/chi-vs-bos-0022400363/play-by-play",
"/game/mil-vs-cle-0022400374/play-by-play",
"/game/okc-vs-mia-0022400375/play-by-play",
"/game/mem-vs-atl-0022400378/play-by-play",
"/game/was-vs-mil-0022400382/play-by-play",
"/game/nyk-vs-nop-0022400384/play-by-play",
"/game/mil-vs-chi-0022400398/play-by-play",
"/game/phx-vs-den-0022400402/play-by-play",
"/game/tor-vs-nyk-0022400397/play-by-play",
"/game/sas-vs-phi-0022400394/play-by-play",
"/game/phi-vs-uta-0022400433/play-by-play",
"/game/sas-vs-mem-0022400863/play-by-play",
"/game/was-vs-cha-0022400860/play-by-play",
"/game/bkn-vs-det-0022400861/play-by-play",
"/game/gsw-vs-phi-0022400864/play-by-play",
"/game/mil-vs-dal-0022400865/play-by-play",
"/game/sac-vs-hou-0022400862/play-by-play",
"/game/tor-vs-orl-0022400870/play-by-play",
"/game/min-vs-phx-0022400873/play-by-play",
"/game/nop-vs-uta-0022400872/play-by-play",
"/game/chi-vs-ind-0022400868/play-by-play",
"/game/okc-vs-sas-0022400871/play-by-play",
"/game/nyk-vs-mia-0022400869/play-by-play",
"/game/por-vs-cle-0022400867/play-by-play",
"/game/lac-vs-lal-0022400874/play-by-play",
"/game/den-vs-bos-0022400866/play-by-play",
"/game/hou-vs-okc-0022400879/play-by-play",
"/game/phi-vs-min-0022400887/play-by-play",
"/game/mil-vs-atl-0022400884/play-by-play",
"/game/gsw-vs-nyk-0022400885/play-by-play",
"/game/cle-vs-chi-0022400886/play-by-play",
"/game/det-vs-lac-0022400898/play-by-play",
"/game/uta-vs-was-0022400894/play-by-play",
"/game/gsw-vs-bkn-0022400901/play-by-play",
"/game/sas-vs-sac-0022400910/play-by-play",
"/game/uta-vs-tor-0022400905/play-by-play",
"/game/det-vs-gsw-0022400919/play-by-play",
"/game/orl-vs-mil-0022400917/play-by-play",
"/game/det-vs-por-0022400926/play-by-play",
"/game/mem-vs-nop-0022400923/play-by-play",
"/game/min-vs-den-0022400952/play-by-play"
]


for i in range(0,len(addresses_list)):
    addresses = addresses_list[i]
    address = "https://www.nba.com" + addresses + "?period=All"
    print(address)
    folder = os.path.join("./../data/" ,address.split("/")[-2])
    
    if not os.path.exists(folder):
        os.mkdir(folder)
        
    url_info = extract_url_information(address)
    
    titles = {}
    counter = 0
    failed = {}
    for url in url_info:
        
        start = time.time()
        random_seconds = np.random.randint(2)#avoid being stopped by remote site
        time.sleep(random_seconds)
        
        try: 
            specific_url = url['url']
            mp4_urls = extract_mp4_urls(specific_url)
            
            mp4_urls = mp4_urls[0]
            
            urllib.request.urlretrieve(mp4_urls, os.path.join(folder,str(counter) + '.mp4'))
            titles[counter] = "Time: " + url["time"] + ", Points: " + url['pts'] + ", Home: " + url['home'] + ", Desc: " + url['info']
            print("done")
        except:
            #retry
            try: 
                
                specific_url = url['url']
                mp4_urls = extract_mp4_urls(specific_url)
                
                mp4_urls = mp4_urls[0]
                
                urllib.request.urlretrieve(mp4_urls, os.path.join(folder,str(counter) + '.mp4'))
                titles[counter] = url
            except:
                print("failed")
                failed[counter] = url
        
        end = time.time()
        
        elapsed = end - start
        print(f"Elapsed time: {elapsed:.2f} seconds")
        print(str(counter) +  " of "  + str(len(url_info)))
        counter = counter+1
        
    with open(os.path.join(folder,'url_info.pkl'), 'wb') as f:
        pickle.dump(url_info, f)
    
    
    with open(os.path.join(folder,'info.pkl'), 'wb') as f:
        pickle.dump(titles, f)
    
    
    with open(os.path.join(folder,'failed.pkl'), 'wb') as f:
        pickle.dump(failed, f)
            