web: gunicorn --pythonpath="$PWD/dnasearch" dnasearch.wsgi

worker: python dnasearch/manage.py rqworker default
