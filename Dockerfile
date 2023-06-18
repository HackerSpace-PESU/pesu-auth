FROM python:3.10.11-bullseye

RUN apt update -y && apt upgrade -y
RUN apt install wget unzip

ARG DEBIAN_FRONTEND=noninteractive
RUN wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
RUN apt install ./google-chrome-stable_current_amd64.deb -y
RUN rm ./google-chrome-stable_current_amd64.deb

RUN pip install get-chrome-driver
RUN get-chrome-driver --auto-download --extract
RUN mv chromedriver/*/bin/chromedriver /usr/bin/chromedriver
RUN chmod +x /usr/bin/chromedriver
RUN rm -rf chromedriver/

COPY app /app
COPY requirements.txt /requirements.txt

RUN pip install -r requirements.txt

CMD ["python", "app/app.py"]