FROM python:3.12-slim
RUN apt-get update && apt-get install -y --no-install-recommends libgdal-dev && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY etl/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY etl etl
COPY database database
ENV PYTHONPATH=/app
CMD ["python","-m","etl","status"]

