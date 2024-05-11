import multiprocessing
import os

# Der Pfad zum Wurzelverzeichnis Ihres Django-Projekts
project_path = os.path.dirname(os.path.abspath(__file__))

# Anzahl der CPU-Kerne multipliziert mit 2 plus 1 für die Anzahl der Arbeiter
workers = multiprocessing.cpu_count() * 2 + 1

# Bind-Adresse und Port
bind = '127.0.0.1:8000'

# Python-Pfad zum Django-Projekt
pythonpath = os.path.join(project_path, 'PlanerDjango')

# Arbeitsverzeichnis (wenn erforderlich)
#chdir = project_path

# Konfiguration der Ausgabedateien
accesslog = os.path.join(project_path, 'gunicorn_access.log')
errorlog = os.path.join(project_path, 'gunicorn_error.log')
