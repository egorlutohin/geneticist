"""
Code adopted from http://djangosnippets.org/snippets/501/
"""

from django.contrib.auth.models import User
from django.conf import settings
import ldap

class ActiveDirectoryBackend:

  def authenticate(self,username=None,password=None):
    if not self.is_valid(username,password):
      return None

    try:
      return User.objects.get(username=username)
    except User.DoesNotExist:
      return None

  def get_user(self,user_id):
    try:
      return User.objects.get(pk=user_id)
    except User.DoesNotExist:
      return None

  def is_valid (self,username=None,password=None):
    ## Disallowing null or blank string as password
    ## as per comment: http://www.djangosnippets.org/snippets/501/#c868
    if password == None or password == '':
      return False
    binddn = "%s@%s" % (username,settings.AD_NT4_DOMAIN)
    try:
      l = ldap.initialize(settings.AD_LDAP_URL)
      l.simple_bind_s(binddn,password)
      l.unbind_s()
      return True
    except ldap.LDAPError:
      return False
