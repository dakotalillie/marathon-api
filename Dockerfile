FROM python:3

VOLUME /app

WORKDIR /app

COPY . .

RUN apt-get -q update && apt-get -qy install netcat
RUN pip install --no-cache-dir -r requirements.txt

ENV FLASK_APP src/app.py
ENV FLASK_ENV development

EXPOSE 5000

CMD python -m src.app
