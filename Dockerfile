# NFC Idea Finder (Tapwise) — runs on the Raspberry Pi 5 (arm64) or any computer
FROM python:3.12-slim
WORKDIR /srv
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY db ./db
COPY app ./app
COPY scripts ./scripts
# The SQLite file (incl. visitor suggestions) lives in /srv/app/data -> mount a volume there
VOLUME /srv/app/data
EXPOSE 8000
CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:8000", "--chdir", "app", "app:app"]
