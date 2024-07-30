FROM python:3-slim

WORKDIR /app

COPY requirements.txt .
COPY local/cert.pem /app/local/
COPY local/key.pem /app/local/
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PORT=8000
ENV DB_HOST=host.docker.internal
ENV DB_USER=root
ENV DB_PASSWORD=rootroot
ENV DB_NAME=taipei_attractions
ENV REDIS_HOST=host.docker.internal

ENTRYPOINT ["/app/entrypoint.sh"]