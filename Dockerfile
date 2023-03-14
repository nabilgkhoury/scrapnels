FROM python:3.11

# upgrade pip setuptools and symlink python to python3
RUN apt-get update -y && \
    apt-get install -y pass sudo telnet vim net-tools

WORKDIR /usr/src/app/scrapnels
# copy code
COPY . .
# install requirements
RUN pip install --no-cache-dir --no-deps -r requirements.txt
# create log directory
RUN mkdir /var/log/scrapnels

ENV PYTHONPATH "${PYTHONPATH}:/usr/src/app/scrapnels"
ENV PATH "${PATH}:/usr/src/app/scrapnels"

# dummy loop just to keep the container up
CMD ["tail", "-f", "/dev/null"]
