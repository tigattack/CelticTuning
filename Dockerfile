FROM python:3.10-alpine

LABEL org.opencontainers.image.authors="tigattack"
LABEL org.opencontainers.image.title="celtictuning"
LABEL org.opencontainers.image.description="Simple Flask app to provide an API and simplified web interface for Celtic Tuning"
LABEL org.opencontainers.image.url="https://github.com/tigattack/Scripts/tree/main/celtictuning"
LABEL org.opencontainers.image.documentation="https://github.com/tigattack/Scripts/blob/main/celtictuning/README.md"
LABEL org.opencontainers.image.source="https://github.com/tigattack/Scripts/tree/main/celtictuning"

EXPOSE 5000

HEALTHCHECK \
  --interval=30s \
  --timeout=10s \
  --start-period=5s \
  --retries=1 \
  CMD ["curl --fail http://localhost:5000/ || exit 1"]

WORKDIR /app

COPY . .

RUN pip3 install -r requirements.txt

ENTRYPOINT ["python3", "-m", "flask", "--app", "celtic_web", "run", "--host", "0.0.0.0"]
