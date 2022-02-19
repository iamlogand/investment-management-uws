web: gunicorn portfoliosite.wsgi
worker: celery -A portfoliosite worker --loglevel=info -P eventlet