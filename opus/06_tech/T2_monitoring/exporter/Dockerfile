FROM python:3.13-slim
WORKDIR /app
COPY node_health_exporter.py /app/node_health_exporter.py
USER 65534:65534
ENV LISTEN_ADDR=0.0.0.0 LISTEN_PORT=9101 PYTHONUNBUFFERED=1
EXPOSE 9101
HEALTHCHECK --interval=30s --timeout=3s --retries=3 \
  CMD python3 -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:9101/healthz', timeout=2).status == 200 else 1)"
ENTRYPOINT ["python3", "/app/node_health_exporter.py"]
