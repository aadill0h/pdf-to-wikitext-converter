# File: Dockerfile (Corrected)

# Use a lean official Python image as a parent image
FROM python:3.11-slim

# Create a directory for the application code
WORKDIR /app

# Install pandoc from the official Debian repositories
RUN apt-get update && \
    apt-get install -y pandoc --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*

# Copy the application script into the /app directory
COPY container_script.py .

# Install Python dependencies
RUN pip install --no-cache-dir pymupdf4llm

# Set the entrypoint to run the script from the /app directory.
# This command will be executed when the container starts.
ENTRYPOINT ["python", "container_script.py"]