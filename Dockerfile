# Base Python 3.11
FROM python:3.11-slim

# Dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libssl-dev \
    tk-dev \
    libffi-dev \
    curl \
    libasound2-dev \
    python3-dev \
    portaudio19-dev \
    ffmpeg \
    libpulse0 \
    alsa-utils \
    pulseaudio \
    && rm -rf /var/lib/apt/lists/*

# app folder
WORKDIR /app

# Copy source to working folder
COPY . /app

# Install python dependencies requirements.txt
RUN pip install --upgrade pip && pip install -r requirements.txt
ARG UID=1000
ARG GID=1000
RUN groupadd -g ${GID} myuser && \
    useradd -m -u ${UID} -g ${GID} myuser

# Switch to the new user
USER myuser

# default command
CMD ["bash"]
