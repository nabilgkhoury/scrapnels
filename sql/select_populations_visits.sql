SELECT year,
       city,
       population,
       SUM(visits) AS visits
FROM museum_stats
JOIN city_stats
USING(city)
WHERE city_stats.population IS NOT NULL
GROUP BY year, city, population