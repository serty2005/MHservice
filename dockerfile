FROM python:3.11.9-slim

WORKDIR /opt/app

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    git \
    tzdata \
    && rm -rf /var/lib/apt/lists/*

RUN pip install -r requirements.txt

RUN git clone https://github.com/serty2005/MHservice.git .

CMD ["python", "/opt/app/app.py"]
