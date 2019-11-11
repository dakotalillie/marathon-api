# Marathon

## Tech Stack

-   Docker
-   Flask
-   Swagger
-   SQLAlchemy
-   PostgreSQL

Code is linted using pylint, formatted using black, and tested using pytest. This app also uses mypy for static typing.

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
