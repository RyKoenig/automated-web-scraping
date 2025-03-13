
import pandas as pd
import numpy as np
import os
from sqlalchemy.sql import text

import sys
import warnings
if not sys.warnoptions:
    warnings.simplefilter("ignore")

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, parent_dir)

from utils import create_db_engine, current_time, get_logger, parse_arguments
from constants import PARENT_DIR, nfl_pfr_team_map


CURRENT_DIR = PARENT_DIR + 'nfl_scraper/'

right_now = current_time()

rb_engine = create_db_engine(db_environment="RB")


def main():

    log = get_logger()
    arguments = parse_arguments()

    if (arguments.season_year == None) & (arguments.season_week == None):
        log.error("You need to add in the season_year you want to upload. eg -y 2024")
        exit(-1)

    cur_year = arguments.season_year

    log = log.bind(
        season_year=cur_year,
    )

    df_snap_counts = pd.read_csv(CURRENT_DIR + f'upload_data/{cur_year}_snap_counts.csv', index_col = None)

    cur_year = df_snap_counts['season_year'].values[0]
    cur_week = df_snap_counts['season_week'].values[0]

    log = log.bind(
        season_year=cur_year,
        season_week=cur_week,
    )

    log.info("Running prf snap count cleaning and uploading")

    df_snap_counts_upload = df_snap_counts[df_snap_counts['already_uploaded'] == False]

    if len(df_snap_counts_upload) > 0:
    
        df_snap_counts_upload['team_id'] = df_snap_counts_upload['team'].replace(nfl_pfr_team_map)

        
        rb_engine = create_db_engine(db_environment="RB")
        
        df_snap_counts_upload = df_snap_counts_upload[['search_year', 'search_week', 'pfr_id', 
                                    'team_id', 'started', 'offensive_snaps', 'defensice_snaps', 'special_teams', 
                                    'player_pos', 'player_name']]
        
        df_snap_counts_upload = df_snap_counts_upload.drop_duplicates(keep = 'first')


        df_snap_counts_upload['player_name'] = df_snap_counts_upload['player_name'].apply(lambda x: x.replace("'", "''"))

        df_snap_counts_upload['player_name'] = df_snap_counts_upload['player_name'].map(lambda x: f"'{x}'")
        df_snap_counts_upload['team_id'] = df_snap_counts_upload['team_id'].map(lambda x: f"'{x}'")
        df_snap_counts_upload['pfr_id'] = df_snap_counts_upload['pfr_id'].map(lambda x: f"'{x}'")
        df_snap_counts_upload['player_pos'] = df_snap_counts_upload['player_pos'].map(lambda x: f"'{x}'")

        log.info("Finally I am adding in the snapcount data to the database...")


        values_string = ",\n".join(["(" + ", ".join(map(str,row)) + ")" for row in df_snap_counts_upload.itertuples(index = False)])


        create_table_query = """
                CREATE TABLE IF NOT EXISTS nfl.snap_counts (
                    season_year INT NOT NULL,
                    season_week INT NOT NULL,
                    pfr_id VARCHAR(20) NOT NULL,
                    team_id UUID NOT NULL,
                    started BOOLEAN,
                    off_snaps INT,
                    def_snaps INT,
                    st_snaps INT,
                    pos VARCHAR(5),
                    player_name VARCHAR(100),
                    PRIMARY KEY (season_year, season_week, pfr_id)
                );
            """
        
        update_games_query = f"""
                            INSERT INTO nfl.snap_counts(season_year, season_week, pfr_id, 
                                                        team_id, started, off_snaps, def_snaps, 
                                                        st_snaps, pos, player_name)
                            VALUES {values_string}
                            ON CONFLICT (season_year, season_week, pfr_id) 
                                    DO UPDATE SET 
                                        team_id = EXCLUDED.team_id,
                                        started = EXCLUDED.started,
                                        off_snaps = EXCLUDED.off_snaps,
                                        def_snaps = EXCLUDED.def_snaps,
                                        st_snaps = EXCLUDED.st_snaps,
                                        pos = EXCLUDED.pos;
                            """
        

        with rb_engine.connect() as conn:
            conn.execute(text("CREATE SCHEMA IF NOT EXISTS nfl;"))
            conn.execute(text(create_table_query))
            conn.execute(text(update_games_query))
            conn.commit()
            

        df_snap_counts['already_uploaded'] = True

        df_snap_counts.to_csv(CURRENT_DIR + f'upload_data/{cur_year}_snap_counts.csv', index = None)


        log.info("Finished running prf snap count cleaning and uploading process")

    else:
        log.info("Finished running prf snap count uploading process. There were no new games to upload")

if __name__ == "__main__":
    main()
