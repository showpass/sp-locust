FROM debian:buster

RUN mkdir /code/
WORKDIR /code/

RUN apt update
RUN apt upgrade -y
RUN apt install -y git gcc python3-dev python3-pip

RUN pip3 install locustio faker

ADD *.py ./
ADD tasks ./tasks
ADD utils ./utils

