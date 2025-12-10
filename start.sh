#!/bin/bash
# Start gunicorn with dynamic PORT from Railway
exec gunicorn --bind 0.0.0.0:${PORT:-5000} --workers 2 --timeout 120 app_sa:app
