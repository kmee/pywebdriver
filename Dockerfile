FROM python:3.9-slim

RUN mkdir -p /app
RUN mkdir -p /etc/pywebdriver

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    libcups2-dev \
    libssl-dev \
    git \
    libusb-1.0-0-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY ./requirements.txt requirements.txt

RUN pip install --upgrade pip

RUN pip install -r requirements.txt

RUN pip install gunicorn

COPY /config/config.ini.tmpl /etc/pywebdriver/config.ini

COPY pywebdriver ./pywebdriver

ENV UDEV=1

# ENTRYPOINT ["tail", "-f", "/dev/null"]

CMD gunicorn pywebdriver:app -b 0.0.0.0:8001 --preload
