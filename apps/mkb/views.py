#coding: utf8
import json

from django.template import RequestContext

from models import Mkb


def mkb(request):
    items = []
    for item in Mkb.objects.filter(level=0):
        items.append({'isLazy': True,
                      'title': item.name,
                      'key': item.pk})
    return RequestContext(json.dumps(items))
