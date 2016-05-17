
Running the webpage offline:

For running the webpage on local server, you need to build a virtual Flask environment
Use command virtualenv flask

download relevant packages
- $ flask/bin/pip install flask
- $ flask/bin/pip install flask-login
- $ flask/bin/pip install flask-mail
- $ flask/bin/pip install flask-sqlalchemy
- $ flask/bin/pip install sqlalchemy-migrate
- $ flask/bin/pip install flask-whooshalchemy
- $ flask/bin/pip install flask-wtf
- $ flask/bin/pip install coverage
- Flask==0.10.1
- Jinja2==2.7.3
- MarkupSafe==0.23
- Werkzeug==0.9.6
- argparse==1.2.1
- itsdangerous==0.24
- rauth==0.7.0
- requests==2.4.3


You may also need to create a database through command line ./db_create.py
(Make sure it is runable. If it does not run, try "chomad a+x db_create.py" first

run "./run.py" .
Then, you may need to put "localhost:5000" to address line in any browsers to see the website



Test:

run ./tests.py on the command line

Result will be shown in the terminal and stored in the coverage folder

