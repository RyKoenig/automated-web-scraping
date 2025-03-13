
import pandas as pd
import numpy as np
from sqlalchemy.sql import text
import os
import sys
import warnings
if not sys.warnoptions:
    warnings.simplefilter("ignore")

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, parent_dir)

from utils import create_db_engine, current_time, get_logger, player_name_no_db_elements
from constants import PARENT_DIR


CURRENT_DIR = PARENT_DIR + 'nba_scraper/'

right_now = current_time()

rb_engine = create_db_engine(db_environment="RB")


def main():

    log = get_logger()

    df_espn_rosters = pd.read_csv(CURRENT_DIR + 'upload_data/delete_espn_roster.csv', index_col = None)

    log.info("Running ESPN roster and uploading")

    if len(df_espn_rosters) > 0:

        rb_engine = create_db_engine(db_environment="RB")

        df_upload = df_espn_rosters[['player_name','espn_id','team_id', 'jersey', 'pos', 'data_pulled']]

        df_upload = df_upload.fillna('NULL')
        
        df_upload = df_upload.drop_duplicates(keep = 'first')

        df_upload['player_name'] = player_name_no_db_elements(df_upload[['player_name']])

        df_upload['player_name'] = df_upload['player_name'].apply(lambda x: x.replace("'", "''"))

        df_upload['player_name'] = df_upload['player_name'].map(lambda x: f"'{x}'")
        df_upload['team_id'] = df_upload['team_id'].map(lambda x: f"'{x}'")
        df_upload['pos'] = df_upload['pos'].map(lambda x: f"'{x}'")
        df_upload['data_pulled'] = df_upload['data_pulled'].map(lambda x: f"'{x}'")

        df_upload = df_upload.replace({np.nan: 'NULL','':'NULL', "'None'": 'NULL', "'NULL'":'NULL'})

        log.info("Finally I am adding in the roster data to the database...")


        values_string = ",\n".join(["(" + ", ".join(map(str,row)) + ")" for row in df_upload.itertuples(index = False)])


        create_table_query = """
                CREATE TABLE IF NOT EXISTS nba.espn_roster (
                    player_name VARCHAR(100) NOT NULL,
                    espn_id INT NOT NULL,
                    team_id UUID NOT NULL,
                    jersey INT,
                    pos VARCHAR(5),
                    data_pulled TIMESTAMP NOT NULL DEFAULT NOW(),
                    PRIMARY KEY (espn_id, team_id, data_pulled)
                );
            """
        
        update_roster_query = f"""
                            INSERT INTO nba.espn_roster (player_name, espn_id, team_id, jersey, pos, data_pulled)
                                VALUES {values_string}
                            ON CONFLICT (espn_id, team_id, data_pulled) 
                            DO UPDATE SET 
                                player_name = EXCLUDED.player_name,
                                jersey = EXCLUDED.jersey,
                                pos = EXCLUDED.pos;
                            """
        
        if len(df_upload) > 0:

            with rb_engine.connect() as conn:
                conn.execute(text("CREATE SCHEMA IF NOT EXISTS nba;"))
                conn.execute(text(create_table_query))
                conn.execute(text(update_roster_query))
                conn.commit()

        log.info("Finished running espn roster uploading process")

    else:
        log.info("Finished running espn roster uploading process. There were no new games to upload")

if __name__ == "__main__":
    main()
