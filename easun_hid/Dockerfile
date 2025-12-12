FROM python:3.11-slim

# Install required system packages
RUN apt-get update && apt-get install -y \
    libusb-1.0-0 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create application directory
WORKDIR /app

# Copy addon files
COPY easun_hid.py /app/
COPY requirements.txt /app/
COPY run.sh /app/

# Install Python dependencies
RUN pip install --no-cache-dir -r /app/requirements.txt

# Make run.sh executable
RUN chmod +x /app/run.sh

# Start the application
CMD ["/app/run.sh"]
