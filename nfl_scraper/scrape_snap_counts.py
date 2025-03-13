import pandas as pd
import numpy as np
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

from utils import current_time, get_logger, parse_arguments
from constants import PARENT_DIR, path_to_chromedriver

CURRENT_DIR = PARENT_DIR + 'nfl_scraper/'

right_now = current_time()

def main():

    try:

        log = get_logger()
        arguments = parse_arguments()

        if (arguments.season_year == None)  & (arguments.season_week == None):
            log.error("You need to add in the season_year, week inputs. eg -y 2024 -w [1-22]")
            exit(-1)

        elif (arguments.season_year == None) | (arguments.season_week == None):
            log.error("You are missing one or more of the following inputs season_year, week inputs. eg -y 2024 -w [1-22]")
            exit(-1)

        cur_year = arguments.season_year
        cur_week = arguments.season_week

        log = log.bind(
            season_year=cur_year,
            season_week=cur_week,
        )

        log.info("Running prf snap count webscrape")

        try:
            df_snap_counts_this_year = pd.read_csv(CURRENT_DIR + f'upload_data/{cur_year}_snap_counts.csv', index_col = None)

            df_snap_counts_this_year['season_week'] = df_snap_counts_this_year['season_week'].astype(str)

            df_snap_counts_this_week = df_snap_counts_this_year[df_snap_counts_this_year['season_week'] == str(cur_week)]

            already_scraped_games = list(df_snap_counts_this_week['team'].unique())

        except:
            df_snap_counts_this_year = pd.DataFrame()
            already_scraped_games = []

            upload_data_path = CURRENT_DIR + "upload_data/"
            os.makedirs(upload_data_path, exist_ok=True)


        #### PFR tries to stop scrapping, so I need to run a few repeat tries to capture all of the games
        repeats = 4

        df_starters = pd.DataFrame()
        df_snap_counts = pd.DataFrame()
        for repeat_count in range(repeats):

            repeat_count = repeat_count * 2

            #### Chromedriver
            service = Service(path_to_chromedriver)
            chrome_options = webdriver.ChromeOptions()

            # ### Ad blocker
            chrome_options.add_argument('--load-extension=/usr/local/share/adblocker')

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

            chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36')

            time.sleep(1)
            driver = webdriver.Chrome(service = service, options = chrome_options)
            time.sleep(2)


            #### I only want to run this once, even when I repeat
            if repeat_count == 0:

                url = f'https://www.pro-football-reference.com/years/{cur_year}/week_{cur_week}.htm'

                driver.get(url)

                time.sleep(5)

                soup = BeautifulSoup(driver.page_source, 'html.parser')

                time.sleep(4)

                games_list_divs = soup.find_all('div', {"class": "game_summaries"})

                if len(games_list_divs) > 1:
                    games_list_divs = [games_list_divs[-1]]

                if len(games_list_divs) == 1:
                    games_list_divs = games_list_divs[0].find_all('div', {"class": "game_summary expanded nohover"})

                df_completed_games = pd.DataFrame()
                for one_game in games_list_divs:
                    
                    try:
                        winner = one_game.find('tr', {"class": "winner"})
                        winner = winner.find('td').get_text()
                    except:
                        #### They posted the game but there is no game data yet
                        continue
                        
                    loser = one_game.find('tr', {"class": "loser"})
                    loser = loser.find('td').get_text()
                    
                    scores = one_game.find_all('td', {"class": "right"})
                    scores = [x.get_text() for x in scores[:3]]
                    scores = [scores[0], scores[-1]]

                    did_away_team_win = one_game.find_all('tr')[1].get("class")[0]


                    if (did_away_team_win == 'winner'):
                        home = winner
                        away = loser
                    elif (did_away_team_win == 'loser'):
                        home = loser
                        away = winner

                    else:
                        log.error("I couldn't find a winner for a game.")
                        exit(-1)
                    
                    away_score = int(scores[0])
                    home_score = int(scores[1])
                
                
                    link = one_game.find('td', {"class": "right gamelink"})
                    link = link.find('a')

                    text = link.get_text()

                    link = link['href']

                    if text == 'Final':
                        data = {'home_team': home,
                                'away_team': away,
                                'home_score': home_score,
                                'away_score': away_score,
                                'link': link}
                            
                        df_completed_games = df_completed_games._append(data, ignore_index = True)

                df_completed_games = df_completed_games[df_completed_games['home_team'].isin(already_scraped_games) == False]

                games_count = len(df_completed_games)

                log.info(f"Number of games to process: {games_count}")


            if games_count > 0:

                for game_num in range(repeat_count, repeat_count + 2):

                    if game_num >= games_count:
                        continue

                    all_snap_counts = []
                    all_starters = []
                    
                    df_one_game = df_completed_games[game_num:game_num+1]
                    
                    link = df_one_game['link'].values[0]

                    main_url = 'https://www.pro-football-reference.com'
                    
                    url = main_url + link
                    
                    home_team = df_one_game['home_team'].values[0]
                    away_team = df_one_game['away_team'].values[0]
                    
                    time.sleep(4)

                    log.info(f"Seach Link {url}")
                        
                    driver.get(url)

                    time.sleep(4)

                    soup = BeautifulSoup(driver.page_source, 'html.parser')
                    
                    log.info(f"Processing {away_team} vs. {home_team}")
                        
                    visitor_starters = soup.find_all('div', {"id": "all_vis_starters"})
                    
                    try:
                        starter_names = visitor_starters[0].find_all('th', {"scope": "row"})
                    except:
                        log.info(f"No snap count data for the {home_team} home game")
                        continue
                        
                    starter_pos = visitor_starters[0].find_all('td', {"class": "left"})


                    # Iterate over the rows and extract the player name and link
                    for n in range(len(starter_names)):
                        player_id = starter_names[n]['data-append-csv']
                        player_name = starter_names[n].get_text()

                        player_pos = starter_pos[n].get_text()

                        data = {'pfr_id':player_id,
                                'player_name':player_name,
                                'player_pos': player_pos}

                        all_starters.append(data)

                    home_starters = soup.find_all('div', {"id": "all_home_starters"})

                    starter_names = home_starters[0].find_all('th', {"scope": "row"})
                    starter_pos = home_starters[0].find_all('td', {"class": "left"})

                    for n in range(len(starter_names)):
                        player_id = starter_names[n]['data-append-csv']
                        player_name = starter_names[n].get_text()

                        player_pos = starter_pos[n].get_text()

                        data = {'pfr_id':player_id,
                                'player_name':player_name,
                                'player_pos': player_pos}

                        all_starters.append(data)

                    #### Now snapcounts

                    visitor_snaps = soup.find_all('div', {"id": "div_vis_snap_counts"})
                    
                    try:
                        players = visitor_snaps[0].find_all('tr', attrs={'data-row': True})
                    except:
                        log.info(f"No starter data for the {home_team} home game")
                        continue

                    # Iterate over the rows and extract the player name and link
                    for n in range(len(players)):
                        try:
                            player_id = players[n].find('th', {"class": "left"})['data-append-csv']
                        except:
                            continue

                        player_name = players[n].find('a').get_text()
                        player_pos = players[n].find('td', {"class": "left"}).get_text()

                        snaps = players[n].find_all('td', {"class": "right"})
                        snaps = [x.get_text() for x in snaps]
                        snaps = [snaps[0], snaps[2], snaps[4]]

                        data = {'team': away_team,
                                'pfr_id':player_id,
                                'player_name':player_name,
                                'player_pos': player_pos,
                                'offensive_snaps': snaps[0],
                                'defensice_snaps':snaps[1],
                                'special_teams': snaps[2]}

                        all_snap_counts.append(data)


                    home_snaps = soup.find_all('div', {"id": "div_home_snap_counts"})

                    players = home_snaps[0].find_all('tr', attrs={'data-row': True})

                    # Iterate over the rows and extract the player name and link
                    for n in range(len(players)):
                        try:
                            player_id = players[n].find('th', {"class": "left"})['data-append-csv']
                        except:
                            continue


                        player_name = players[n].find('a').get_text()
                        player_pos = players[n].find('td', {"class": "left"}).get_text()

                        snaps = players[n].find_all('td', {"class": "right"})
                        snaps = [x.get_text() for x in snaps]
                        snaps = [snaps[0], snaps[2], snaps[4]]

                        data = {'team': home_team,
                                'pfr_id':player_id,
                                'player_name':player_name,
                                'player_pos': player_pos,
                                'offensive_snaps': int(snaps[0]),
                                'defensice_snaps':int(snaps[1]),
                                'special_teams': int(snaps[2])}

                        all_snap_counts.append(data)

                    df_starters = df_starters._append(all_starters)
                    df_snap_counts = df_snap_counts._append(all_snap_counts)

                    starters_list = list(df_starters['pfr_id'].unique())

                    conditions = [df_snap_counts['pfr_id'].isin(starters_list)]
                    choice = [True]

                    df_snap_counts['started'] = np.select(conditions, choice, default = False)

                    df_snap_counts['season_year'] = cur_year
                    df_snap_counts['season_week'] = cur_week
                    df_snap_counts['already_uploaded'] = False


                    df_snap_counts_this_year = df_snap_counts_this_year._append(df_snap_counts)

                    ### We want to save it like this everytime to reduce needing to rescrape games.
                    ### PRF actively try to prevent websraping.

                    df_snap_counts_this_year.to_csv(CURRENT_DIR + f'upload_data/{cur_year}_snap_counts.csv', index = None)

                log.info(f"Finished searching for snap counts for week {cur_week}")

            else:
                log.info(f"All games this week have already been scraped")

            driver.quit()

    except Exception as e:

        log.info(f"Error encountered: {e}")

        log.info("Executing chrome cleaning script...")

        # Run your Bash script
        subprocess.run([PARENT_DIR + "kill_chrome.sh"], check=True)


if __name__ == "__main__":
    main()
