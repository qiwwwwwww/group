#!/usr/bin/python
import sys
import logging
logging.basicConfig(stream=sys.stderr)
sys.path.insert(0,"/var/www/flask_work/flask_work/")

from app import app as application
application.secret_key = 'Add your secret key'
