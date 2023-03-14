#!/usr/bin/env python
import logging
import os
from pathlib import Path
from dotenv import load_dotenv
from logging.config import fileConfig
import argparse

from scrapnels import __version__ as package_version
from museum_visits import scrape_museum_visits, analyze_museum_visits

load_dotenv()
POSTGRES_USER = os.getenv('POSTGRES_USER')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD')
POSTGRES_HOST = os.getenv('POSTGRES_HOST')
POSTGRES_PORT = os.getenv('POSTGRES_PORT')
OUTPUT_PATH = os.getenv('OUTPUT_PATH')

fileConfig('logging.ini')
logger = logging.getLogger(__name__)

parser = argparse.ArgumentParser(
    prog='scrapnels',
    description=f'Scrapnels (v{package_version})',
    usage=f"{os.linesep}scrapnels-cli -h"
          f"{os.linesep}scrapnels-cli -v"
          f"{os.linesep}scrapnels-cli demo -h"
)
parser.add_argument('-v',
                    '--version',
                    action='version',
                    version=f'%(prog)s {package_version}')
sub_parsers = parser.add_subparsers(title="subcommands",
                                    dest="subcommand",
                                    description="valid scrapnels subcommands",
                                    help='additional help')
sql_uri = f"user={POSTGRES_USER} " \
          f"password={POSTGRES_PASSWORD} " \
          f"host={POSTGRES_HOST} " \
          f"port={POSTGRES_PORT}"
demo_parser = sub_parsers.add_parser(
    'demo',
    description='scrape museum visits and local population then correlate them',
    usage=f"{os.linesep}scrapnels-cli demo -h"
          f"{os.linesep}scrapnels-cli demo"
          f"{os.linesep}scrapnels-cli demo"
          f" --sql 'user=postgres password=postgres host=localhost port=5432'"
)
demo_parser.add_argument('-s',
                         '--sql',
                         type=str,
                         default=sql_uri,
                         help=f'sql connection uri (default: {sql_uri})')
demo_parser.add_argument('-o',
                         '--output',
                         type=Path,
                         default=Path(OUTPUT_PATH),
                         help=f'output path on local file system'
                              f' (default: {OUTPUT_PATH})')

args = parser.parse_args()
if args.subcommand == 'demo':
    scrape_museum_visits(sql_uri=args.sql)
    analyze_museum_visits(sql_uri=args.sql, output_path=args.output)
else:
    parser.print_help()
