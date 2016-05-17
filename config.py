import os
basedir = os.path.abspath(os.path.dirname(__file__))

CSRF_ENABLED = True
SECRET_KEY = 'we-are-awesome-group'

#sql database setting
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')
WHOOSH_BASE = os.path.join(basedir, 'search.db')

# email server
MAIL_SERVER = 'smtp.gmail.com'
MAIL_PORT = 25
MAIL_USE_TLS = False
MAIL_USE_SSL = False
MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')

# administrator list
ADMINS = ['qwictest@gmail.com']

# pagination
POSTS_PER_PAGE = 3
MAX_SEARCH_RESULTS = 50

#OAUTH_CREDENTIALS
OAUTH_CREDENTIALS = {
    'facebook': {
        'id': '1605450336371205',
        'secret': 'ceb588e7ce31b3c43496138f85cf97ec'
    },
    'google': {
    'id': '1096619265421-gvips9nrkie806rpomfekaldgc0dglhu.apps.googleusercontent.com',
    'secret': 'LKmtYXc7du9gVpV7Q7CoSXZa'
}
}

# file upload
UPLOAD_FOLDER= 'uploads/'
ALLOWED_EXTENSIONS= set(['txt', 'pdf'])
UPLOAD_FOLDER= UPLOAD_FOLDER
MAX_CONTENT_LENGTH = 16 * 1024 * 1024

