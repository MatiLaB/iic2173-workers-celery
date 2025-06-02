# ./project/Dockerfile (anteriormente ./django-docker/app/Dockerfile, pero siguiendo tu docker-compose.yml)
FROM python:3.11

# Instala herramientas de diagnóstico de red (ping, netcat, telnet)
# Esto es crucial para depurar problemas de conectividad desde dentro del contenedor.
RUN apt-get update && apt-get install -y iputils-ping netcat-openbsd telnet && rm -rf /var/lib/apt/lists/*

# set work directory
WORKDIR /app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install dependencies
RUN pip install --upgrade pip
COPY requirements.txt /app/
RUN pip install -r /app/requirements.txt
# copy project
COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]