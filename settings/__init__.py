from .base import *
from .local_settings import *

try:
    AD_NT4_DOMAIN, AD_DNS_NAME # used in authentication ldap backend
except:
    pass
else:
    LDAP = True
    AD_LDAP_URL = 'ldap://%s:%d' % (AD_DNS_NAME, AD_LDAP_PORT)
    AUTHENTICATION_BACKENDS = ('django.contrib.auth.backends.ModelBackend', 'hotline.adauth.ActiveDirectoryBackend')

