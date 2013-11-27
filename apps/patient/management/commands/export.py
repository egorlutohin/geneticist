#coding: utf8
import re
from datetime import date, timedelta

import pyExcelerator
from django.core.management.base import BaseCommand, CommandError

from common_helpers import nested_commit_on_success
from patient.models import Visit, Patient, Diagnosis
from user_profile.models import CustomUser


USER_CHANGED = CustomUser.objects.filter(mo__code=540011)[0]


def get_mkb(excel_page):
    """ Из данных на странице 2 создает словарь.
        Ключ -- полное название диагноза
        значение -- код по МКБ """
    CODE = 0
    NAME = 1
    info = {}
    expr = re.compile(r'[A-Z]\d+(\.\d+)*')
    for num_row in range(5, 256):
        name_index = (num_row, NAME)
        name = excel_page.get(name_index)
        if name is None:
            continue
        name = name.replace("del(15)(q11-13)", '').strip()
        cell_index = (num_row, CODE,)
        code = excel_page.get(cell_index)
        if code is None:
            print u'exclude %s' % name
            continue
        info[name] = code.strip()
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
    if u'Пробанд' in unicode(type_patient):
        return Patient.PROBAND
    return Patient.FETUS


def get_type_residence(type_residence):
    if not type_residence:
        return 1  # Новосибирск
    type_residence = type_residence.lower()
    if u'новосибирская область' in type_residence:
        return 2
    elif u'новосибирск' in type_residence:
        return 1
    return 3


def get_gender(gender):
    """ заолняем пол """
    gender = gender.lower()
    if u'мужской' in gender:
        return 1
    elif u'женский' in gender:
        return 2
    return 4  # не известно


def get_date(xldate):
    if xldate:
        return date(1899, 12, 30) + timedelta(days=xldate)
    return None


def get_patient_info(excel_page, num_row, diagnosis_info):
    """ Создает информацию о пациенте без диагноза"""
    last_name = excel_page.get((num_row, 4), '')
    if not last_name:
        return {}
    social_st = excel_page.get((num_row, 19), '')
    type_resid = excel_page.get((num_row, 20), '')
    type_p = excel_page.get((num_row, 18), '')
    gender = excel_page.get((num_row, 21), '')
    #  информация о пациенте
    date_reg_xl = get_date(excel_page.get((num_row, 24)))
    info_p = {'last_name': last_name,
              'first_name': excel_page.get((num_row, 5), ''),
              'patronymic': excel_page.get((num_row, 6), ''),
              'birthday': get_date(excel_page.get((num_row, 7))),
              'death': get_date(excel_page.get((num_row, 8))),
              'seria_policy': excel_page.get((num_row, 15), ''),
              'number_policy': excel_page.get((num_row, 16), ''),
              'code_insurance_company': int(excel_page.get((num_row, 17), '')) or '',
              'registration': excel_page.get((num_row, 14), ''),
              'code_allocate_mo': excel_page.get((num_row, 22), ''),
              'name_allocate_mo': excel_page.get((num_row, 23), ''),
              'social_status': get_social_status(social_st),
              'type_residence': get_type_residence(type_resid),
              'type': get_type(type_p),
              'gender': get_gender(gender),
              'diagnosis_text': diagnosis_info.get('name', ''),
              'diagnosis_text_code': diagnosis_info.get('code', ''),
              'added_by': Patient.ADDED_BY_CHOICES[1][0],
              'date_registration': date_reg_xl or date.today(),
              'user_changed': USER_CHANGED}
    return info_p


def get_diagnosis_info(excel_page, num_row, mkb):
    """ Возвращает информацию о диагнозе """
    name = excel_page.get((num_row, 2))
    if name:
        name = name.strip()
        code = mkb.get(name)
        date_reg_xl = get_date(excel_page.get((num_row, 24)))
        if code:
            return {'code': code,
                    'name': name,
                    'date_created': date_reg_xl or date.today(),
                    'user_changed': USER_CHANGED}
    return {}


class Command(BaseCommand):
    help = u"Export from patients.xls into database https://github.com/dicos/geneticist/issues/47"

    @nested_commit_on_success
    def handle(self, *args, **options):
        book = pyExcelerator.parse_xls("excel.xls")
        patient_excel = book[0][1]
        diagnosis_excel = book[1][1]
        mkb = get_mkb(diagnosis_excel)
        for num_row in range(2, 2238):
            d_info = get_diagnosis_info(patient_excel, num_row, mkb)
            p_info = get_patient_info(patient_excel, num_row, d_info)
            if not p_info:
                continue
            patient = Patient(**p_info)
            patient.save()
            if not d_info:
                print patient_excel.get((num_row, 2))
                raise Exception(u'Нет информации по пациенту')
            d_info['patient'] = patient
            diagnosis = Diagnosis(**d_info)
            diagnosis.save()
