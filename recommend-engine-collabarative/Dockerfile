FROM python:3.12-slim

RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpython3-dev \
    && pip install --upgrade pip

WORKDIR /app

COPY requirements.txt /app/requirements.txt

RUN pip install -r /app/requirements.txt

COPY recommend-engine-collabarative /app

CMD ["python", "main.py"]
