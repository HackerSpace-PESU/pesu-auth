FROM python:3.10.11-bullseye

RUN apt update -y && apt upgrade -y

COPY app /app
COPY README.md /README.md
COPY requirements.txt /requirements.txt

RUN pip install -r requirements.txt

CMD ["python", "app/app.py"]