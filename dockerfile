FROM python:3.11.9-slim


RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    git \
    tzdata \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /opt/app

RUN git clone https://github.com/serty2005/MHservice.git .

ENV TZ="Europe/Moscow"

ENV SDKEY=&SDKEY

RUN pip install -r requirements.txt

CMD ["python", "/opt/app/app.py"]