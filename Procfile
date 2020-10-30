web: gunicorn --pythonpath="$PWD/dnasearch" config.wsgi:application

worker: python dnasearch/manage.py rqworker default
