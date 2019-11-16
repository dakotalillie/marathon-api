.PHONY: start-dev, stop-dev, start-ci, stop-ci, tests, db-shell

ARGS=$(filter-out $@,$(MAKECMDGOALS))
DOCKER_COMPOSE_DEV=docker-compose -f docker/docker-compose.dev.yml
DOCKER_COMPOSE_CI=docker-compose -f docker/docker-compose.ci.yml

start-dev:
	$(DOCKER_COMPOSE_DEV) up $(ARGS)

stop-dev:
	$(DOCKER_COMPOSE_DEV) down $(ARGS)

start-ci:
	$(DOCKER_COMPOSE_CI) up $(ARGS)

stop-ci:
	$(DOCKER_COMPOSE_CI) down $(ARGS)

tests:
	docker exec marathon-api python -m pytest $(ARGS)

db-shell:
	docker exec -itu postgres postgres psql

# this is necessary for $(ARGS) to work
%:
	@:
