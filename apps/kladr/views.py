#coding: utf8
import json

from models import Kladr, Doma, Street, Socr
from models import REGION_LEVEL, DISTRICT_LEVEL, CITY_LEVEL, VILAGE_LEVEL




def get_socr_dict(level):
    return dict([(v.socr, v.name) for v in Socr.objects.filter(level=level)])


def get_kladr(level, code_startwith=""):
    qs = Kladr.objects.filter(code__endswith="00", level=level)
    if len(code_startwith):
        qs = qs.filter(code__startwith=code_startwith)
    return qs


def get_regions(request):
    """ Список регионов """
    info = []
    socr = get_socr_dict(REGION_LEVEL)
    for region in get_kladr(REGION_LEVEL):
        info.append({{'id': region.get_region_code(),
                      'value': socr[region.socr]}})
    return json.dumps(info)


def get_districts(request):
    """ Список регионов """
    info = []
    socr = get_socr_dict(DISTRICT_LEVEL)
    region_code = request.GET['region_code']
    for district in get_kladr(DISTRICT_LEVEL, region_code):
        info.append({{'id': district.get_district_code(),
                      'value': socr[district.socr]}})
    return json.dumps(info)


def get_cities(request):
    """ Список регионов """
    info = []
    socr = get_socr_dict(CITY_LEVEL)
    district_code = request.GET['district_code']
    for city in get_kladr(CITY_LEVEL, district_code):
        info.append({{'id': city.get_city_code(),
                      'value': socr[city.socr]}})
    return json.dumps(info)


def get_street(request):
    """ Список улиц """
    info = []
    socr = get_socr_dict()
    city_code = request.GET['city_code']
    streets_qs = Street.objects.filter(code__endswith='00', code__startswith=city_code)
    for street in streets_qs:
        info.append({'id': stret.get_street_code(),
                     'value': socr[street.socr]})
    return json.dumps(into)
