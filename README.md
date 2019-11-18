# Marathon API

_This repo is a work in progress_

Marathon is a task-managing app, similar to Jira or Trello. This is a practice project for me to refamiliarize myself with backend development after spending my days at work as a frontend developer.

Features currently up and running:

-   JWT authentication
-   CRUD for the User resource
-   CRUD for the Team resource
-   CI via Jenkins

More features are on the way &mdash; you can see some of the tasks I have planned on the [Kanban Project board](https://github.com/dakotalillie/marathon-api/projects/1).

## Tech Stack

This app is built using:

-   Python 3.8
-   Flask
-   SQLAlchemy
-   PostgreSQL
-   Docker
-   Swagger
-   Jenkins

The code is linted using pylint, formatted using black, and tested using pytest.

I intend for this to adhere to the [JSON-API](https://jsonapi.org/) standard, although more work needs to be done to ensure full compliance.

## Development Setup

Make sure you have Make, Docker and Docker Compose installed. Copy the `env/sample.dev.env` file to a new file, `.env`, in the project root. Then run:

```bash
make start-dev
```

Or if you want to run the app in the background:

```bash
make start-dev -- -d
```

This will build the image for the app locally and start the following containers:

-   A development API server, running on port 5000
-   A swagger UI server, running on port 8080
-   A postgres server, running on port 5432

(The swagger UI docs were mostly using for endpoint planning and mapping out a crude domain model. They are not currently up to date, though I intend on updating them soon.)

To stop the containers, you can run:

```bash
make stop-dev
```

## Accessing the Database

To gain terminal access to postgres, you can run:

```bash
make db-shell
```

Note that the data is not currently being persisted to a volume &mdash; if you kill the postgres container and start a new one, you'll be back to a blank slate. This is intentional for early development.

## Tests

To run tests, first make sure the `marathon-api` and `postgresql` containers are running. Then run:

```
make tests
```
