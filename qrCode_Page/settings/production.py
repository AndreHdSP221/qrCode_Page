from .settings import *

SECRET_KEY = '4caacb77c4d137e28f47f5d7c786b30e0ea6e13509e9b350e51a9f8a6bef46e2'

DATABESES = {
	'default' : {
		'ENGINE' : 'django.db.backends.mysql',
		'NAME' : 'Nome',
		'USER' : 'User',
		'PASSWORD' : 'Senha',
		'HOST' : 'Host',
		'PORT' : 'Porta',
	}
}
