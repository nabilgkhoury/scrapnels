CREATE TABLE IF NOT EXISTS city_stats
(
    city       VARCHAR(128) NOT NULL,
    population BIGINT       NULL,
    PRIMARY KEY (city)
);