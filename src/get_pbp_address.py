from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import urllib
import urllib.request
import urllib.parse
import numpy as np

def extract_url_information(url):
    """Extracts URL information from a webpage using Selenium.

    Args:
        url (str): The URL of the webpage to extract information from.

    Returns:
        list: A list of dictionaries containing URL information.
    """


    options = Options()
    options.add_argument('--headless')  # Run in headless mode
    driver = webdriver.Chrome()  # Replace with your preferred WebDriver
    driver.get(url)

    # Wait for the page to load
    random_seconds = np.random.randint(0, 1)
    wait = WebDriverWait(driver, random_seconds)
    wait.until(EC.presence_of_element_located((By.TAG_NAME, 'body')))

    # Extract URL information from visible elements
    visible_urls = [a.get_attribute('href') for a in driver.find_elements(By.TAG_NAME, 'a') if a.is_displayed()]

    # Extract URL information from hidden elements using JavaScript
    hidden_urls = driver.execute_script("""
    return Array.from(document.querySelectorAll('a')).filter(a => {
        const rect = a.getBoundingClientRect();
        return rect.width === 0 || rect.height === 0 || rect.top < 0 || rect.left < 0 || rect.bottom > window.innerHeight || rect.right   
     > window.innerWidth;
        }).map(a => a.href);
    """)

    # Combine visible and hidden URLs
    all_urls = visible_urls + hidden_urls

    # Extract additional information from each URL (e.g., domain, path, query parameters)
    url_info = []
    for url in all_urls:
        parsed_url = urllib.parse.urlparse(url)
        if(  "/game/" in parsed_url.path and "box-score" not  in parsed_url.path):
            if parsed_url.path not in url_info:
                url_info.append(parsed_url.path + "/play-by-play")

    driver.quit()
    return url_info


import datetime


# start_date = datetime.datetime(2023, 10, 10)
# end_date = datetime.datetime(2024, 1, 1)
# Set the start date and end date

start_date = datetime.datetime(2024, 12, 15)
end_date = datetime.datetime(2024, 12, 31)

# Generate a list of dates from start_date to end_date
dates = [start_date + datetime.timedelta(days=x) for x in range((end_date - start_date).days + 1)]

start_date = datetime.datetime(2025, 3, 1)
end_date = datetime.datetime(2025, 3, 15)

# Generate a list of dates from start_date to end_date
dates = dates + [start_date + datetime.timedelta(days=x) for x in range((end_date - start_date).days + 1)]

# Format the dates as "2024-03-25"
formatted_dates = [date.strftime('%Y-%m-%d') for date in dates]

print(formatted_dates)
all_info ={}

for d in formatted_dates:
    print(d)
    url_info = extract_url_information("https://www.nba.com/games?date=" + d)
    all_info[str(d)] = list(set(url_info))

list_2024 = []
list_2025 = []

for k in all_info.keys():
    infos = all_info[k]
    if "2024" in k:
        list_2024 = list_2024 + infos
    else:
        list_2025 = list_2025 + infos

list_2024_teams = []
summary_2024 = []
home_2024 = []
list_2025_teams = []
summary_2025 = []
home_2025 = []

for l in list_2024:
    raw = l.split("/")[2]
    raw = raw.split("-")[0:-1]
    key = raw[0] + "-" +  raw[-1]
    key2 = raw[-1] + "-" +  raw[0]
    home = raw[-1]
    if (key not in summary_2024) and( key2 not in summary_2024) and (home not in home_2024):
        list_2024_teams.append([raw[0] + "-" +  raw[-1],l,raw[0],raw[-1]])
        summary_2024.append(key)
        home_2024.append(home)
    
for l in list_2025:
    raw = l.split("/")[2]
    raw = raw.split("-")[0:-1]
    key = raw[0] + "-" +  raw[-1]
    key2 = raw[-1] + "-" +  raw[0]
    home = raw[-1]
    if ((key not in summary_2025) and( key2 not in summary_2025) and (home not in home_2025) and
    (key not in summary_2024) and( key2 not in summary_2024)):
        list_2025_teams.append([raw[0] + "-" +  raw[-1],l,raw[0],raw[-1]])
        summary_2025.append(key)
        home_2025.append(home)
    
final_list = []

for l in list_2024_teams:
    final_list.append(l[1])
    
for l in list_2025_teams:
    final_list.append(l[1])
    
#NOTE: the output are variable which will be copied in other scripts

    