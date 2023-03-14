import typing
import logging
from pathlib import Path
from dataclasses import dataclass

import requests
from bs4 import BeautifulSoup
import psycopg

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn import linear_model

logger = logging.getLogger(__name__)

# constants
MUSEUMS_URL = "https://en.wikipedia.org/wiki/List_of_most-visited_museums"
RECREATE_CITY_STATS = open('sql/recreate_city_stats.sql', 'r').read()
RECREATE_MUSEUM_STATS = open('sql/recreate_museum_stats.sql', 'r').read()
SELECT_POPULATIONS_VISITS = open('sql/select_populations_visits.sql', 'r').read()


@dataclass
class MuseumVisitStat:
    museum: str  # museum name (ex: 'Louvre')
    city: str  # unique city name/last fragment of wiki url (ex: 'Paris')
    year: int  # year visited (ex: 2022)
    visits: int  # number of visits that year

    @classmethod
    def scrape(cls) -> typing.Generator['MuseumVisitStat', None, None]:
        museums_html = requests.get(MUSEUMS_URL).content
        museums_soup = BeautifulSoup(museums_html, 'html.parser')
        yearly_tables = museums_soup.find_all('table', class_='wikitable')

        # Scrape Yearly Museum Visits
        # TODO: handle invalid year values
        years = [int(year.text.strip())
                 for year in museums_soup.select("h3 > span.mw-headline")]

        logger.info(f"found years: {years}")
        for year, yearly_table in zip(years, yearly_tables):
            logger.info(f"scraping museum visits for year {year}")
            museums = [museum_a.text.strip()
                       for museum_a
                       in yearly_table.select("tr > td:nth-of-type(1) > a")]
            logger.debug(f"scraped museums: {museums}")
            cities = [city_a['href'].strip().rsplit('/', 1)[-1]
                      for city_a
                      in yearly_table.select("tr > td:nth-of-type(2) > a:nth-of-type(1)")]
            logger.debug(f"scraped cities: {cities}")
            visit_stats = [int(visit_count_td.next_element.replace(',', '').strip())
                           for visit_count_td
                           in yearly_table.select("tr > td:nth-of-type(3)")]
            logger.debug(f"scraped yearly museum visits: {visit_stats}")

            # TODO: replace assert with warning log message
            assert len(museums) == len(cities) == len(visit_stats), \
                   "scraped entities must match in number!"

            for museum, city, visits in zip(museums, cities, visit_stats):
                yearly_visits = MuseumVisitStat(museum, city, year, visits)
                logger.debug(f"generated {yearly_visits}")
                yield yearly_visits


@dataclass
class CityStat:
    populationByCity = {}  # class cache
    city: str  # unique city name/last fragment of wiki url (ex: 'Paris')
    population: int  # city population based on most recent stats

    @classmethod
    def scrape(cls, city_key: str) -> 'CityStat':
        city_pretty = city_key.replace("_", " ")
        city_url = f"https://en.wikipedia.org/wiki/{city_key}"
        logger.debug(f"scraping population of city {city_pretty} at {city_url}")
        city_html = requests.get(city_url).content
        city_soup = BeautifulSoup(city_html, 'html.parser')
        city_infobox = city_soup.select_one("table.infobox")
        pop_header_tr = city_infobox.find(
            lambda tag: (tag.name == 'tr' and
                         tag.th and
                         tag.th.text.startswith("Population") or
                         False)
        )

        # if tr.th has a sibling td, we use it. Otherwise use td under sibling of tr
        pop_header_tr_td = pop_header_tr.th.find_next_sibling()
        if pop_header_tr_td:
            pop_value_str = pop_header_tr_td.find(text=True).strip()
            try:
                pop_value = int(pop_value_str.split(' ', 1)[0].replace(',', ''))
            except ValueError as exc:
                pop_value = None
                logger.warning(f"failed to scrape {city_url}: {exc}")
        else:
            pop_value_tr = pop_header_tr.find_next_sibling()
            pop_value_str = pop_value_tr.td.find(text=True).strip()
            try:
                pop_value = int(pop_value_str.split(' ', 1)[0].replace(',', ''))
            except ValueError as exc:
                pop_value = None
                logger.warning(f"failed to scrape {city_url}: {exc}")

        # cache population
        cls.populationByCity[city_key] = pop_value
        logger.debug(f"{city_pretty} population = {pop_value}")
        return CityStat(city=city_key, population=pop_value)


def scrape_museum_visits(sql_uri: str):
    logger.info(f"scraping museum visits...")
    # TODO: handle failed connections with logging
    sql_connection = psycopg.connect(sql_uri, autocommit=False)
    sql_cursor = sql_connection.cursor()

    # recreate relevant SQL tables
    sql_cursor.execute(RECREATE_CITY_STATS)
    sql_cursor.execute(RECREATE_MUSEUM_STATS)
    logger.info(f"recreated related SQL tables")

    # scrape and insert museum visit stats and local population
    inserted_cities = 0
    inserted_museums = 0
    for museum_stat in MuseumVisitStat.scrape():
        if museum_stat.city not in CityStat.populationByCity:
            # Scrape City Population, but only if not found
            city_stat = CityStat.scrape(museum_stat.city)
            sql_cursor.execute('INSERT INTO city_stats VALUES(%s, %s)',
                               (city_stat.city, city_stat.population))
            inserted_cities += 1
            logger.debug(f"inserted {city_stat}")

        sql_cursor.execute('INSERT INTO museum_stats VALUES(%s, %s, %s, %s)',
                           (museum_stat.museum,
                            museum_stat.city,
                            museum_stat.year,
                            museum_stat.visits))
        inserted_museums += 1
        logger.debug(f"inserted {museum_stat}")

    logger.info(f"inserted {inserted_cities} cites and {inserted_museums} museums")
    # commit changes and close db connection
    sql_connection.commit()
    sql_cursor.close()
    sql_connection.close()


def analyze_museum_visits(sql_uri: str, output_path: Path):
    """
    Determine and plot correlation between city population and museum visits

    :param sql_uri:
    :param output_path:
    :return:
    """
    logger.info(f"analyzing museum visits...")
    # TODO: handle failed connections with logging
    sql_connection = psycopg.connect(sql_uri, autocommit=False)
    sql_cursor = sql_connection.cursor()
    sql_cursor.execute(SELECT_POPULATIONS_VISITS)
    results = sql_cursor.fetchall()
    logger.debug(f"loaded {len(results)} results")
    # close db connection
    sql_cursor.close()
    sql_connection.close()

    # load population/visit data
    pop_visits = pd.DataFrame(results,
                              columns=['year', 'city', 'population', 'visits'])
    logger.info(f"loaded {len(pop_visits)} data points")

    # prepare model training set
    pop_visits_X = np.array(pop_visits["population"], ndmin=2).T
    pop_visits_y = np.array(pop_visits["visits"], ndmin=2).T

    # train linear-regression model
    logger.info(f"training linear regression model...")
    regr = linear_model.LinearRegression()
    regr.fit(pop_visits_X, pop_visits_y)
    pop_visits_y_predicted = regr.predict(pop_visits_X)

    # show scatter-plot of valid population-visit data points vs model predictions
    figure_path = output_path / "city-populations-museum-visits.png"
    logger.debug(f"generating figure {figure_path}...")
    plt.scatter(pop_visits['population'], pop_visits['visits'])
    plt.plot(pop_visits['population'], pop_visits_y_predicted, color="black")
    plt.title("real data vs linear regression model")
    plt.xlabel("City Population")
    plt.ylabel("Museum Visits")
    plt.savefig(figure_path)
    logger.info(f"saved figure {figure_path}")
