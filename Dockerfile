FROM python:3.7-slim as builder
COPY requirements.txt /app/requirements.txt
WORKDIR /app
RUN pip install -r requirements.txt

FROM builder
COPY . /app
WORKDIR /app
CMD ["python", "main.py"]