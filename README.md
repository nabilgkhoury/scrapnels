# Scrapnels
clone git repo and cd into it
```shell
dev$ git clone https://github.com/nabilgkhoury/scrapnels.git 
dev$ cd scrapnels
```

### Dot-Env File:
copy `scrapnels/env` to `scrapnels/.env` and edit as per your system. 
pay close attention to `SHARE_PATH`. This is where the demo figure will be saved.
### Docker Suite Launch:
- start docker daemon as per your system
- launch docker suite
```shell
scrapnels$ make all
```

### Scrapnels Usage:
- ssh to `scrapnels` container:
```shell
scrapnels$ docker exec -it scrapnels /bin/bash
root@scrapnels#
```
- run `scrapnels-cli` help:
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
root@scrapnels# scrapnels-cli demo --help
usage: 
scrapnels-cli demo -h
scrapnels-cli demo
scrapnels-cli demo --sql 'user=postgres password=postgres host=localhost port=5432'

scrape museum visits and local population then correlate them

options:
  -h, --help            show this help message and exit
  -s SQL, --sql SQL     sql connection uri (default: user=postgres password=postgres host=localhost port=5432)
  -o OUTPUT, --output OUTPUT
                        output path on local file system (default: /tmp/scrapnels)
```
- run the demo without arguments. `--sql` and `--output` arguments are optional and will default to dot-env file.
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
note the path where the figure was saved. 
based on our docker volume setup, the figure path exists on docker host too.
- examine `scrapnels` logs:
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

- access output:
    - close ssh session (ex: `CTRL-D`)
    - open the generated figure:
```shell
open /tmp/scrapnels/city-populations-museum-visits.png
```
