# encoding: utf8
from .base import *
from .local_settings import *

LDAP = False

try:
    AD_NT4_DOMAIN, AD_DNS_NAME, AD_SEARCH_DN # used in authentication ldap backend
except:
    pass
else:
    LDAP = True
    AD_LDAP_URL = 'ldap://%s:%d' % (AD_DNS_NAME, AD_LDAP_PORT)
    AUTHENTICATION_BACKENDS = ('auth.adauth.ActiveDirectoryBackend',)
    LDAP_PERMISSION_GROUP = {
        'user': 'ГРП_Пользователь',
        'admin': 'ГРП_Администратор'
    }

