FROM python:3

VOLUME /app

WORKDIR /app

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

ENV FLASK_APP src/app.py
ENV FLASK_ENV development

EXPOSE 5000

CMD python -m src.app
