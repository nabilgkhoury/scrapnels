IMAGE := scrapnels-scrapnels
CONTAINER := scrapnels
TAG := latest

.PHONY: help all stop clean rebuild build run restart kill

help: ## list make targets
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

.DEFAULT_GOAL := help

all: stop build create start ## stop, build, create and start

stop: ## stop related docker containers
	$(info Make: Stopping "$(CONTAINER)" Docker Container...)
	docker container stop $(CONTAINER) || true
	$(info Make: Stopping Compose Containers)
	docker-compose stop

clean: stop ## stop related docker containers and clean related docker containers and images
	$(info Make: Removing "$(IMAGE)" Docker Image...)
	docker image rm  --force $(IMAGE)
	$(info Make: Removing Compose Containers)
	docker-compose rm --stop --force
	$(info Make: Removing Compose Images and Orphan Containers)
	docker-compose down --rmi all --remove-orphans

rebuild: clean ## clean and build related docker images
	$(info Make: Rebuilding "$(IMAGE)" Docker Image...)
	docker image build --tag $(IMAGE) . --rm --file ./Dockerfile
	$(info Make: Rebuilding Compose Images...)
	docker-compose build --force-rm --no-cache

build: ## build related docker images
	$(info Make: Building "$(IMAGE)" Docker Image...)
	docker build --tag $(IMAGE) . --file Dockerfile
	$(info Make: Building Compose Images...)
	docker-compose build

create: ## create related docker containers
	$(info Make: Creating Compose Containers...)
	docker-compose up --no-start --remove-orphans

start: ## start related docker containers
	$(info Make: Starting Compose Comtainers...)
	docker-compose up --detach --no-build

restart: stop start ## restart related docker containers

run: create start ## run related docker containers

kill: ## kill related docker containers
	$(info Make: Killing "$(CONTAINER)" Docker Container...)
	docker container kill $(CONTAINER)
	$(info Make: Killing Compose Containers...)
	docker-compose kill