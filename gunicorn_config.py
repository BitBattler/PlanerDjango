from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

static_path = str(BASE_DIR / 'static')
static_url_path = '/static'

def when_ready(server):
    server.log.info("Gunicorn is ready to serve static files.")

def post_request(worker, req, *args):
    if req.path.startswith(static_url_path):
        req.path = req.path[len(static_url_path):]

bind = '0.0.0.0:8002'
workers = 3
timeout = 30
accesslog = '-' # Log to stdout

# Serve static files
static_map = [
    f"{static_url_path} {static_path}"
]

command = ' '.join([
    "gunicorn",
    f"--bind {bind}",
    f"--workers {workers}",
    f"--timeout {timeout}",
    f"--access-logfile {accesslog}",
    *static_map
])
