# syntax=docker/dockerfile:1

FROM python:3.8-slim-buster
WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

EXPOSE 9944

COPY app.py .
RUN mkdir files

CMD [ "python3", "app.py"]
