FROM python:3.8

RUN apt-get update && apt-get install -y \
    libffi-dev \
    libnacl-dev \
    build-essential \
    && pip install wheel


RUN apt-get install -y ffmpeg

WORKDIR /app

COPY ./requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt

COPY . /app

CMD ["python", "-u", "/app/wham.py"]
