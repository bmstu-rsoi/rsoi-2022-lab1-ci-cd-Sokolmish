FROM python

RUN pip install \
    flask \
    flask_api \
    psycopg2 \
    requests

COPY src/ /app/

WORKDIR /app

CMD [ "python3", "/app/main.py" ]
