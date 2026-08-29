FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .

RUN groupadd --gid 10001 guardian \
    && useradd --uid 10001 \
               --gid guardian \
               --no-create-home \
               --shell /usr/sbin/nologin \
               guardian

RUN chown -R guardian:guardian /app

USER 10001:10001

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
