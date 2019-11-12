# Marathon API

_This repo is a work in progress_

Marathon will be a task-managing app, similar to Jira or Trello. This is a practice project for me to refamiliarize myself with backend-development after largely spending my time at work as a frontend developer.

## Tech Stack

This app is built using:

-   Python >= 3.6
-   Flask
-   SQLAlchemy
-   PostgreSQL
-   Docker
-   Swagger

The code is linted using pylint, formatted using black, and tested using pytest.

I intend for this to adhere to the [JSON-API](https://jsonapi.org/) standard, although more work needs to be done to ensure full compliance.

## Development Setup

Make sure you have Docker installed. Then run:

```bash
docker-compose up
```

This launches several containers:

-   A development API server, running on port 5000
-   A swagger UI server, running on port 8080
-   A postgres server, running on port 8181

To gain terminal access to postgres, you can run:

```bash
docker exec -itu postgres postgres psql
```

The data for the database will be refreshed every time a new instance of the postgres container is spun up.

## Directory Structure

`initdb.d` is a directory containing scripts that will be run by the development PostgreSQL server upon startup.

## Tests

To run test, source the virtual environment and run:

```bash
python3 -m pytest
```
