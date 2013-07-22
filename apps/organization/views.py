from models import Organization

from django.shortcuts import render_to_response
from django.template import RequestContext

def mo_list(request):
    
    response = {'orgs': Organization.objects.all()}
    return render_to_response('organization/list.html',
                              response,
                              context_instance=RequestContext(request))

