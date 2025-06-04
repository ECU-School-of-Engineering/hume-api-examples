# Usa una imagen base oficial con Python 3.11
FROM python:3.11-slim

# Instala dependencias del sistema necesarias para compilar paquetes y reproducir audio
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
    && rm -rf /var/lib/apt/lists/*

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copia tu código fuente al contenedor
COPY . /app

# Instala dependencias si tienes un requirements.txt
# Descomenta esta línea si es necesario
# RUN pip install --upgrade pip && pip install -r requirements.txt

# Comando por defecto (reemplázalo si usas un script específico)
CMD ["python"]
