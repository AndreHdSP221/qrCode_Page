from .settings import *

DEBUG = True

SECRET_KEY = "68d2b3272b850c446985a2b8bb4c1f8c4fb4b361af23ca1a5cbc58120751bebf"

ALLOWED_HOSTS = ['127.0.0.1']

DATABASES = {
	'default' : {
		'ENGINE' : 'django.db.backends.sqlite3',
		'NAME' : os.path.join(BASE_DIR, 'db.sqlite3'),
	}
}
