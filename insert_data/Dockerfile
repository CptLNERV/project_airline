FROM python:3.8

WORKDIR /app

COPY requirements.txt .

ENV PIP_NO_CACHE_DIR=false

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "insert_data.py"]
