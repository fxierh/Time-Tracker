import multiprocessing
import os

bind = ":8000"
workers = multiprocessing.cpu_count() * 2 + 1

# Production
if os.environ.get('DEBUG') == 'False':
    accesslog = None
    errorlog = None
    preload_app = True

# Local development with or without docker
else:
    # Log to stdout
    accesslog = '-'
    errorlog = '-'

    # Restart workers when code changes. This setting is intended for development.
    reload = True
    reload_extra_files = ["./templates/", "./templates/registration", "./classic_tracker/templates/classic_tracker/"]
