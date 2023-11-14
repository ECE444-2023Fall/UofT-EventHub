# syntax-docker/dockerfile:1

FROM python:3.9-slim
WORKDIR /
COPY ../requirements.txt requirements.txt
RUN apt-get update 
RUN apt-get -y install gcc
RUN pip install --upgrade pip
RUN pip3 install -r requirements.txt
RUN apt-get update && apt-get install -y tzdata
ENV TZ=America/New_York
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
COPY . .
ENV FLASK_APP=app/main.py 
CMD ["python3", "-m", "flask", "run", "--host=0.0.0.0"]