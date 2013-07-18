# encoding: utf8
"""
Code adopted from http://djangosnippets.org/snippets/501/
"""

import ldap

from django.contrib.auth import get_user_model
from django.conf import settings

from organization.models import Organization

User = get_user_model()

class ActiveDirectoryBackend:

  def authenticate(self,username=None,password=None):
      
    lc = ldap.initialize(settings.AD_LDAP_URL)
    lc.set_option(ldap.OPT_NETWORK_TIMEOUT, 10.0)
    if not self.is_valid(lc, username, password):
      return None
      
    result = lc.search_s(settings.AD_SEARCH_DN, ldap.SCOPE_SUBTREE, 'sAMAccountName=%s' % username, ['memberOf', 'givenName', 'sn', 'displayName'])
    lc.unbind_s()
    
    if len(result) > 0:
        result = result[0][1]
    else:
        return None
    
    #~ import ptb; ptb.set_trace()
    
    first_name = result['givenName'][0]
    last_name = result['sn'][0]
    patronymic = result['displayName'][0] # L G N
    try:
        patronymic = patronymic.split()[2]
    except:
        patronymic = ''
        
    memberOf = result['memberOf'] # list of strings 'CN=lpu-users-nokvd,OU=Users,DC=example,DC=com
    
    if len(memberOf) > 0:
        _ = []
        for i in memberOf:
            _.append(i.split(',')[0][3:])
            
        memberOf = _
    else:
        return None

    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        user = User()
        user.username = username
        
    
        
    if settings.LDAP_PERMISSION_GROUP['admin'] in memberOf:
        user.is_staff = True
        user.is_superuser = True
    elif settings.LDAP_PERMISSION_GROUP['user'] in memberOf:
        pass
    else:
        return None
        
    orgs = Organization.objects.filter(ldap_name__in=memberOf)
    if len(orgs) > 0:
        user.mo = orgs[0]
    else:
        user.mo = None
        
    user.first_name = first_name
    user.last_name = last_name
    user.patronymic = patronymic
        
    user.save()
    return user

  def get_user(self,user_id):
    try:
        return User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return None

  def is_valid (self, l, username=None,password=None):
    ## Disallowing null or blank string as password
    ## as per comment: http://www.djangosnippets.org/snippets/501/#c868
    if password == None or password == '':
        return False
    binddn = "%s@%s" % (username,settings.AD_NT4_DOMAIN)
    try:
        l.simple_bind_s(binddn,password)
        return True
    except ldap.SERVER_DOWN:
        raise Exception(u'Сервер авторизации не доступен')
    except ldap.LDAPError:
        return False
