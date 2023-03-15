# Scrapnels
clone git repo and cd into it
```shell
dev$ git clone https://github.com/nabilgkhoury/scrapnels.git 
dev$ cd scrapnels
```

## 1. Editing Dot-Env File:
copy `scrapnels/env` to `scrapnels/.env` and edit as per your system. 
pay close attention to `SHARE_PATH`. This is where the demo figure will be saved.
```shell
# example '.env' file for *nix-compatible hosts
POSTGRES_HOST=postgres  # name of postgres container
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
SHARE_PATH=/tmp  # share path on docker host
OUTPUT_PATH=/tmp/scrapnels  # output path on docker guest
```
**NOTE:** `.env` file is consumed by:
- docker via `docker-compose.yml`
- scrapnels-cli code (`scrapnels/cli.py`) via `dotenv` package

## 2. Launching Docker Suite:
### 2.1. start docker daemon
as per your system
### 2.2. launch docker suite:
```shell
scrapnels$ make all
```
**TIP:** `make all` can be broken down into two steps:
- `make build`, which builds docker images: `postgres:12.9` and `scrapnels-scrapnels`
- `make run`, which creates the corresponding docker containers:
  `postgres` and `scrapnels` then starts them.

## 3. Using Scrapnels:
### 3.1. ssh to `scrapnels` container
```shell
scrapnels$ docker exec -it scrapnels /bin/bash
root@scrapnels#
```

### 3.2. view `scrapnels-cli` help
```shell
root@scrapnels# scrapnels-cli --help
usage: 
scrapnels-cli -h
scrapnels-cli -v
scrapnels-cli demo -h

Scrapnels (v1.2023-MAR)

options:
  -h, --help     show this help message and exit
  -v, --version  show program's version number and exit

subcommands:
  valid scrapnels subcommands

  {demo}         additional help
```

### 3.3. view `scrapnels-cli demo` help
```shell
root@scrapnels# scrapnels-cli demo --help
usage: 
scrapnels-cli demo -h
scrapnels-cli demo
scrapnels-cli demo --sql 'user=postgres password=postgres host=localhost port=5432'

scrape museum visits and local population then correlate them

options:
  -h, --help            show this help message and exit
  -s SQL, --sql SQL     sql connection uri (default: user=postgres password=postgres host=postgres port=5432)
  -o OUTPUT, --output OUTPUT
                        output path on local file system (default: /tmp/scrapnels)
```
`--sql` and `--output` command line arguments are optional.
their respective default values are determined based on the dot-env file.  

### 3.4. run demo `scrapnels-cli demo`
#### 3.4.1. run unit-tests
```shell
scrapnels$ python -m unittest -v
test_museum_stats_2019 (test.test_museum_visits.MuseumVisitsTestCase.test_museum_stats_2019) ... ok
test_museum_stats_2020 (test.test_museum_visits.MuseumVisitsTestCase.test_museum_stats_2020) ... ok
test_museum_stats_2021 (test.test_museum_visits.MuseumVisitsTestCase.test_museum_stats_2021) ... ok
test_museum_stats_2022 (test.test_museum_visits.MuseumVisitsTestCase.test_museum_stats_2022) ... ok
test_paris_city_stat (test.test_museum_visits.MuseumVisitsTestCase.test_paris_city_stat) ... ok

----------------------------------------------------------------------
Ran 5 tests in 0.994s

OK
```
#### 3.4.2. run the demo without arguments:
```shell
root@scrapnels# scrapnels-cli demo
INFO - scraping museum visits...
INFO - recreated related SQL tables
INFO - found years: [2022, 2021, 2020, 2019]
INFO - scraping museum visits for year 2022
INFO - scraping museum visits for year 2021
WARNING - failed to scrape https://en.wikipedia.org/wiki/Changsha: invalid literal for int() with base 10: '10.2393\u2002million'
INFO - scraping museum visits for year 2020
INFO - scraping museum visits for year 2019
WARNING - failed to scrape https://en.wikipedia.org/wiki/Melbourne: invalid literal for int() with base 10: '4917750\xa0(2021)'
INFO - inserted 43 cites and 75 museums
INFO - analyzing museum visits...
INFO - loaded 48 data points
INFO - training linear regression model...
INFO - saved figure /tmp/scrapnels/city-populations-museum-visits.png
```
**TIP:** note the path where the figure was saved. 

Based on our docker volume setup, the figure path exists on docker host too.

### 3.5. examine logs and view output:
#### 3.5.1. examine logs
```shell
root@scrapnels# ls -ltra /var/log/scrapnels
drwxr-xr-x 1 root root  4096 Mar 14 12:30 ..
drwxr-xr-x 1 root root  4096 Mar 14 12:33 .
-rw-r--r-- 1 root root 40349 Mar 14 12:36 scrapnels.log
-rw-r--r-- 1 root root 40349 Mar 14 12:36 museum_visits.log
```
you'll find a demo-specific log `museum-visits.log`.
`museum_visits.log` gets replaced every time the demo is run 
while `scrapnels.log` is a rotating log that gets appended to.

#### 3.5.2. view output
- close ssh session (ex: `CTRL-D`)
- open the generated figure:
```shell
open /tmp/scrapnels/city-populations-museum-visits.png
```

## 4. Cleaning up After Demo
To clean up all related docker artefacts once done with the demo:
```shell
scrapnels$ make clean
```

**TIP:** To list all `make` options:
```shell
scrapnels$ make help
help                           list make targets
all                            stop, build, create and start
stop                           stop related docker containers
clean                          stop related docker containers and clean related docker containers and images
rebuild                        clean and build related docker images
build                          build related docker images
create                         create related docker containers
start                          start related docker containers
restart                        restart related docker containers
run                            run related docker containers
kill                           kill related docker containers
```
