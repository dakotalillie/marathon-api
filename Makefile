.PHONY: start-dev, stop-dev, start-ci, stop-ci, tests, db-shell, lint, black

ARGS=$(filter-out $@,$(MAKECMDGOALS))
DOCKER_COMPOSE_DEV=docker-compose -f docker/docker-compose.dev.yml
DOCKER_COMPOSE_CI=docker-compose -f docker/docker-compose.ci.yml
TARGET_DIRS=src test

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

lint:
	docker exec marathon-api pylint --load-plugins pylint_flask,pylint_flask_sqlalchemy $(TARGET_DIRS) $(ARGS)

black:
	docker exec marathon-api black $(TARGET_DIRS) $(ARGS)

# this is necessary for $(ARGS) to work
%:
	@:
