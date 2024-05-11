# Verwende ein offizielles Python Runtime als Eltern-Image
FROM python:3.11.2

RUN pip install --upgrade pip
# Setze das Arbeitsverzeichnis im Container
WORKDIR /PlanerDjango

# Kopiere die lokalen Konfigurationsdateien in das Container
COPY requirements.txt ./

# Installiere alle benötigten Pakete
RUN pip install --no-cache-dir -r requirements.txt

# Kopiere den restlichen Anwendungscode
COPY . .

# Mache den Port, auf dem die App läuft, nach außen sichtbar
EXPOSE 800

# Setzen Sie die Umgebungsvariable für Django
ENV DJANGO_SETTINGS_MODULE=Planer.settings


# Starten Sie den Server beim Start des Containers
CMD ["gunicorn", "Planer.wsgi:application", "--bind", "0.0.0.0:8000"]