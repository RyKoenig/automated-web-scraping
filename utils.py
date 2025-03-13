import logging
from logging.handlers import RotatingFileHandler
import structlog
import sys
import sqlalchemy
import os
import argparse
from pytz import timezone
from unidecode import unidecode
from datetime import datetime
from dotenv import load_dotenv, find_dotenv
import warnings
if not sys.warnoptions:
    warnings.simplefilter("ignore")


def configure_logging():

    log_formatter = logging.Formatter("%(message)s")

    # Console handler (prints to terminal)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_formatter)

    # Rotating file handler (keeps 5 log files, each max 5MB)
    file_handler = RotatingFileHandler("snap_counts.log", maxBytes=5*1024*1024, backupCount=5)
    file_handler.setFormatter(log_formatter)

    # Get the root logger and configure handlers
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)

    structlog.configure(
        processors=[
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M.%S"),
            structlog.dev.ConsoleRenderer(colors=False),
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

configure_logging()

def get_logger():
    return structlog.get_logger()


def create_db_engine(db_name=None, db_environment="RB"):

    load_dotenv(find_dotenv())
    if db_name == None:
        db_name = os.environ.get("{0}_DB_NAME".format(db_environment))
    else:
        db_environment = db_name

    engine = sqlalchemy.create_engine(
        "postgresql://{0}:{1}@{2}:{3}/{4}".format(
            os.environ.get("{0}_DB_USER".format(db_environment)),
            os.environ.get("{0}_DB_PASSWORD".format(db_environment)),
            os.environ.get("{0}_DB_HOST".format(db_environment)),
            os.environ.get("{0}_DB_PORT".format(db_environment)),
            db_name,
        )
    )

    return engine


def parse_arguments():
    """Parses command-line arguments for the script."""
    parser = argparse.ArgumentParser(description="Create field goal efficacy customizations")
    
    parser.add_argument(
        "--season_year",
        "-y",
        type=int,
        help="The season year of the games, in YYYY format.",
    )
    parser.add_argument(
        "--season_week",
        "-w",
        type=int,
        help="The season week of the games.",
        choices=range(1, 19),
        metavar="season_week",
    )

    arguments = parser.parse_args()

    return arguments 



def current_time():
    right_now = datetime.now(tz = timezone('US/Eastern')).replace(tzinfo=None)
    return right_now



def player_name_no_db_elements(corpus_file):
    corpus_file.columns = [0]
    corpus_file[0] = corpus_file[0].astype(str)
    corpus_file[0] = corpus_file[0].apply(lambda x: x.replace('*', ''))
    corpus_file[0] = corpus_file[0].apply(lambda x: unidecode(x))
    corpus_file[0] = corpus_file[0].apply(lambda x: x.replace("'", "''"))
    corpus_file[0] = corpus_file[0].apply(lambda x: x.lstrip())
    corpus_file[0] = corpus_file[0].apply(lambda x: x.rstrip())
    return(corpus_file)
