DROP TABLE IF EXISTS city_stats CASCADE;
CREATE TABLE city_stats
(
    city       VARCHAR(128) NOT NULL,
    population BIGINT       NULL,
    PRIMARY KEY (city)
);