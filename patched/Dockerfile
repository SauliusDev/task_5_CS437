FROM python:3.9-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    libmagic1 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN python init_db.py
RUN python populate_db.py

EXPOSE 5001

ENV FLASK_APP=app/app.py
ENV PYTHONUNBUFFERED=1

CMD ["python", "run.py"]

