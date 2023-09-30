FROM python:3.9-slim-buster

RUN apt-get update && apt-get install -y \
    build-essential \
    nmap \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir /code
WORKDIR /code

COPY requirements.txt .
RUN python3.9 -m pip install --no-cache-dir --upgrade \
    pip \
    setuptools \
    wheel
RUN python3.9 -m pip install --no-cache-dir \
    -r requirements.txt
COPY . .

CMD ["python3.9", "main.py", "--mode=PROD"]