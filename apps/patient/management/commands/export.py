#coding: utf8
import re
from datetime import date

import pyExcelerator
from django.core.management.base import BaseCommand, CommandError

from common_helpers import nested_commit_on_success
from patient.models import Visit, Patient, Diagnosis


def get_mkb(excel_page):
    """ Из данных на странице 2 создает словарь.
        Ключ -- полное название диагноза
        значение -- код по МКБ """
    CODE = 0
    NAME = 1
    info = {}
    expr = re.compile(r'[A-Z]\d+(\.\d+)*')
    for num_row in range(3, 254):
        name_index = (num_row, NAME)
        name = excel_page.get(name_index)
        if name is None:
            continue
        cell_index = (num_row, CODE,)
        code = excel_page.get(cell_index)
        if code is None:
            print u'exclude %s' % name
            continue
        info[code] = name
    return info


def get_social_status(status):
    """ Преобразует значение соц. статуса из экселя в 
        бд. генетического реестра """
    if not status:
        return 14  # Не определео
    status = status.lower()
    childrens = (u'дошкольник', u'ребенок',)
    for i in childrens:
        if i in status:
            return 1  # Дошкольник, см Patient.SOCIAL_STATUSES
    if u'школьник' in status:
        return 4  # Школьник
    elif u'пенсионер' in status:
        return 12
    return 14  # не определено


def get_type(type_patient):
    """ Преобразует значение ячеек колонки ProbandПробанд экселя
        в поле тип пациента """
    if not type_patient:
        return 1  # Новосибирск
    type_patient = type_patient.lower()
    if u'новосибирск' in type_patien:
        return 1
    elif u'новосибирская область' in type_patient:
        return 2
    return 3


def get_gender(gender):
    """ заолняем пол """
    gender = gender.lower()
    if u'мужской' in gender:
        return 1
    elif u'женский' in gender:
        return 2
    return 4  # не известно


def get_patient_info(excel_page, num_row):
    """ Создает информацию о пациенте без диагноза"""
    social_st = excel_page.get((num_row, 21), '')
    type_p = excel_page.get((num_row, 22), '')
    gender = excel_page.get((nm_row, 23), '')
    #  информация о пациенте
    info_p = {'last_name': excel_page.get((num_row, 4), ''),
              'first_name': excel_page.get((num_row, 5), ''),
              'patronymic': excel_page.get((num_row, 6), ''),
              'birthday': excel_page.get((num_row, 7)),
              'death': excel_page.get((num_row, 8)),
              'seria_policy': excel_page.get((num_row, 15), ''),
              'number_policy': excel_page.get((num_row, 16), ''),
              'code_insurance_company': excel_page.get((num_row, 17), ''),
              'registration': excel_page.get((num_row, 14), ''),
              'code_allocate_mo': excel_page.get((num_row, 24), ''),
              'name_allocate_mo': excel_page.get((num_row, 25), ''),
              'social_status': get_social_status(social_st),
              'type': get_type(type_p),
              'gender': get_gender(gender),
              'date_registration': excel_page.get((num_row, 27), date.today()),}
    #  информация о диагнозе
    info_d = {}
    return info_p, info_d


class Command(BaseCommand):
    help = u"Export from patients.xls into database https://github.com/dicos/geneticist/issues/47"

    @nested_commit_on_success
    def handle(self, *args, **options):
        book = pyExcelerator.parse_xls("patients.xls")
        patient_info = book[0]
        diagnosis_info = book[1]
