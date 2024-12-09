# Use Gitleaks image
FROM zricethezav/gitleaks:latest as gitleaks-base

# Use Python
FROM python:3.10-alpine3.16

# Install the dependencies
RUN pip install --no-cache-dir pydantic

# Install Git
RUN apk add --no-cache git

# Copy the script
COPY gitleaks_detection.py /app/gitleaks_detection.py

# Copy Gitleaks binary
COPY --from=gitleaks-base /usr/bin/gitleaks /usr/bin/gitleaks

# Set the working directory
WORKDIR /app

# Default command to run Python script
ENTRYPOINT ["python", "/app/gitleaks_detection.py"]
