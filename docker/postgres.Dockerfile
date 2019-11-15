FROM postgres

COPY ./initdb.d /docker-entrypoint-initdb.d
