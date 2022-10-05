# Docker file for local development
FROM ubuntu:22.04

# Install python 3.10.6 & pip
RUN apt-get update
RUN apt-get install -y python3.10 python3-pip python3.10-venv

# Install MySQL client
RUN apt-get install -y mysql-client libmysqlclient-dev

# Install requirements
WORKDIR /home/time_tracker
COPY requirements.txt .
RUN python3.10 -m venv venv/
# Activate virtual environment (effect lasts in further commands & docker compose)
ENV PATH="/home/time_tracker/venv/bin:$PATH"
RUN pip install -r requirements.txt

# Copy code
COPY . .

# For local development
EXPOSE 8000
