DROP TABLE IF EXISTS museum_stats CASCADE;
CREATE TABLE museum_stats
(
    museum VARCHAR(256) NOT NULL,
    city   VARCHAR(128) NOT NULL,
    year   SMALLINT     NOT NULL,
    visits BIGINT       NOT NULL,
    PRIMARY KEY (museum, city, year),
    CONSTRAINT fk_city
        FOREIGN KEY (city)
            REFERENCES city_stats (city)
);