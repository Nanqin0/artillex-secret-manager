FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/
# optional：COPY scripts/ ./scripts/

EXPOSE 8000


CMD ["gunicorn","app.main:app","-w","4","-k","uvicorn.workers.UvicornWorker","--bind","0.0.0.0:8000"]