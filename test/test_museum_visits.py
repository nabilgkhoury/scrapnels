import unittest

from scrapnels import museum_visits

MILLION = 1000*1000


class MuseumVisitsTestCase(unittest.TestCase):
    museumStats = list(museum_visits.MuseumStat.scrape())

    def test_museum_stats_2022(self):
        # count 2022 visits
        count_2022 = sum(map(lambda stat: stat.year == 2022, self.museumStats))
        self.assertEqual(count_2022, 9)
        count_2022_paris = sum(
            map(lambda stat: stat.year == 2022 and stat.city.startswith('Paris'),
                self.museumStats)
        )
        self.assertEqual(count_2022_paris, 3)

    def test_museum_stats_2021(self):
        count_2021 = sum(map(lambda stat: stat.year == 2021, self.museumStats))
        self.assertEqual(count_2021, 42)
        count_2021_paris = sum(
            map(lambda stat: stat.year == 2021 and stat.city.startswith('Paris'),
                self.museumStats)
        )
        self.assertEqual(count_2021_paris, 3)

    def test_museum_stats_2020(self):
        count_2020 = sum(map(lambda stat: stat.year == 2020, self.museumStats))
        self.assertEqual(count_2020, 8)
        count_2020_paris = sum(
            map(lambda stat: stat.year == 2020 and stat.city.startswith('Paris'),
                self.museumStats)
        )
        self.assertEqual(count_2020_paris, 1)

    def test_museum_stats_2019(self):
        count_2019 = sum(map(lambda stat: stat.year == 2019, self.museumStats))
        self.assertEqual(count_2019, 16)
        count_2019_paris = sum(
            map(lambda stat: stat.year == 2019 and stat.city.startswith('Paris'),
                self.museumStats)
        )
        self.assertEqual(count_2019_paris, 0)

    def test_paris_city_stat(self):
        paris_stat = museum_visits.CityStat.scrape('Paris')
        self.assertTrue(20*MILLION > paris_stat.population > 2*MILLION)


if __name__ == '__main__':
    unittest.main()
