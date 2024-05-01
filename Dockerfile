# Verwende ein offizielles Python Runtime als Eltern-Image
FROM python:3.9-slim

# Setze das Arbeitsverzeichnis im Container
WORKDIR /app

# Kopiere die lokalen Konfigurationsdateien in das Container
COPY requirements.txt ./

# Installiere alle benötigten Pakete
RUN pip install --no-cache-dir -r requirements.txt

# Kopiere den restlichen Anwendungscode
COPY . .

# Mache den Port, auf dem die App läuft, nach außen sichtbar
EXPOSE 8000

# Definiere die Umgebungsvariablen (falls nötig)
ENV NAME World

# Führe die Anwendung aus
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
