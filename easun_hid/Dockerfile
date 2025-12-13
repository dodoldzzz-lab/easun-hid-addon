FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    libusb-1.0-0 \
    usbutils \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY easun_hid.py requirements.txt run.sh /app/

RUN pip install --upgrade pip && pip install -r requirements.txt

RUN chmod +x /app/run.sh

CMD ["/app/run.sh"]
