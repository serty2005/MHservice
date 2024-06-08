FROM python:3.11.9-slim

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    tzdata \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /opt/app

ENV TZ="Europe/Moscow"

RUN pip install -r requirements.txt

CMD ["python", "/opt/app/app.py"]