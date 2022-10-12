import multiprocessing
import os

bind = ":8000"
workers = multiprocessing.cpu_count() * 2 + 1

# Production
if os.environ.get('DEBUG') == 'False':
    preload_app = True
    accesslog = "/home/time_tracker/log/access.log"
    errorlog = "/home/time_tracker/log/error.log"

# Local development with or without docker
else:
    accesslog = "/dev/stdout"
    errorlog = "/dev/stdout"

    # Restart workers when code changes. This setting is intended for development.
    reload = True
    reload_extra_files = ["./templates/", "./templates/registration", "./classic_tracker/templates/classic_tracker/"]
