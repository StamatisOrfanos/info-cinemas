FROM python:3.7.8
RUN apt update -y
RUN apt upgrade -y
RUN mkdir /InfoCinemas

WORKDIR /InfoCinemas

COPY requirements.txt .
COPY app.py .
COPY users.json .
COPY movies.json .

ADD templates ./templates
ADD static ./static
ADD methods ./methods
ADD models ./models 
ADD lib ./lib

RUN pip install -r requirements.txt

ENTRYPOINT [ "python", "-u", "app.py" ]
