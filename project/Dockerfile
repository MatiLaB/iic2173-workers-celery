# ./django-docker/app/Dockerfile
FROM python:3.11

# set work directory
WORKDIR /opt/

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install dependencies
COPY requirements.txt ./
RUN pip install --upgrade pip && pip install -r requirements.txt
# copy project
COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]