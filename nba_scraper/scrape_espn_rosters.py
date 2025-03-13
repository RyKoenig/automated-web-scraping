import pandas as pd
import re
import urllib.request
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import subprocess
import time
import sys
import os
import warnings
if not sys.warnoptions:
    warnings.simplefilter("ignore")

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, parent_dir)

from utils import current_time, get_logger
from constants import PARENT_DIR, path_to_chromedriver, nba_espn_team_map

CURRENT_DIR = PARENT_DIR + 'nba_scraper/'

right_now = current_time()

# This method finds the urls for each of the rosters in the NBA using regexes.
def build_team_urls():
    # Open the espn teams webpage and extract the names of each roster available.
    f = urllib.request.urlopen('https://www.espn.com/nba/teams')
    teams_source = f.read().decode('utf-8')
    teams = dict(re.findall("/nba/team/_/name/(\w+)/(.+?)\",", teams_source))

    # Using the names of the rosters, create the urls of each roster
    roster_urls = []
    for key in teams.keys():
        # each roster webpage follows this general pattern.
        roster_urls.append('https://www.espn.com/nba/team/roster/_/name/' + key + '/' + teams[key])
        teams[key] = str(teams[key])
    return dict(zip(teams.values(), roster_urls))


def main():

    try:

        log = get_logger()

        log.info("Running ESPN NBA roster webscrape")

        roster_urls = build_team_urls()


        #### Chromedriver
        service = Service(path_to_chromedriver)
        chrome_options = webdriver.ChromeOptions()

        # ### Ad blocker
        # chrome_options.add_argument('--load-extension=/usr/local/share/adblocker')

        chrome_options.add_argument('--headless')
        chrome_options.add_argument("--window-size=1920x1080")
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--disable-software-rasterizer')
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")

        prefs = {
            "profile.managed_default_content_settings.images": 2,  # Block images
            "profile.managed_default_content_settings.ads": 2  # Block Ads
        }
        chrome_options.add_experimental_option("prefs", prefs)


        time.sleep(1)
        driver = webdriver.Chrome(service = service, options = chrome_options)
        time.sleep(2)



        df_everyone = pd.DataFrame()
        count = 3
        for key, url in roster_urls.items():

            if count > 0:
                count = count - 1
            else:
                continue

            time.sleep(1)
            
            driver.get(url)

            time.sleep(2)

            log.info(f"Scraping the {key} roster")

            soup = BeautifulSoup(driver.page_source, 'html.parser')

            table = soup.find('div', {"class": 'ResponsiveTable Team Roster Roster__MixedTable'}) 
            
            columns = table.find_all('th', {'class': 'Table__TH'})
            
            roster_columns = [x.get_text().lower() for x in columns]

            roster_columns += ['player_name', 'href', 'team']
            
            rows = soup.find_all('tr', {"class": 'Table__TR Table__TR--lg Table__even'}) 
            
            all_rows = []
            for r in range(len(rows)):
            
                one_row = rows[r]
            
                data = [x.get_text() for x in one_row]

                img_tag = one_row.find('img', {'title': True})
                if img_tag:
                    data += [img_tag['title']]
                else:
                    data += ['']

                name_tag = one_row.find('a', {'class': 'AnchorLink'})
                if name_tag:
                    data += [name_tag['href']]
                else:
                    data += ['']

                data += [key]

                all_rows.append(data)
            
            
            df_one_team = pd.DataFrame(data = all_rows, columns = roster_columns)

            df_everyone = df_everyone._append(df_one_team, ignore_index = True)


        df_everyone['jersey'] = df_everyone['name'].str.extract(r'(\d+)$')

        del df_everyone['name']

        df_everyone['espn_id'] = df_everyone['href'].apply(lambda x: x.split('/')[-2])

        del df_everyone['href']

        df_everyone['team_id'] = df_everyone['team'].replace(nba_espn_team_map)

        del df_everyone['team']
        del df_everyone['']


        df_everyone = df_everyone[['player_name','espn_id','team_id','age','ht', 'wt', 'college', 'jersey', 'pos', 'salary']]

        df_everyone['data_pulled'] = str(right_now.date())


        upload_data_path = CURRENT_DIR + "upload_data/"
        os.makedirs(upload_data_path, exist_ok=True)

        df_everyone.to_csv(CURRENT_DIR + 'upload_data/delete_espn_roster.csv', index = None)
        driver.quit()

        log.info(f"Finished scraping ESPN NBA rosters")

    except Exception as e:

        log.info(f"Error encountered: {e}")

        log.info("Executing chrome cleaning script...")

        # Run your Bash script
        subprocess.run([PARENT_DIR + "kill_chrome.sh"], check=True)


if __name__ == "__main__":
    main()
