#coding: utf8
import json

from django.http import HttpResponse

from models import Mkb


def is_folder(item):
    return (item.lft + 1) < item.rght


def mkb(request):
    items = []
    mkb_qs = Mkb.objects.all()
    if 'key' in request.GET:
        mkb_qs = mkb_qs.filter(parent=request.GET['key'])
    else:
        mkb_qs = mkb_qs.filter(level=0)
    for item in mkb_qs:
        items.append({'isLazy': True,
                      'title': unicode(item),
                      'key': item.pk,
                      'isFolder': is_folder(item)})
    return HttpResponse(json.dumps(items))
