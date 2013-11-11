#coding: utf8
from django import template

from patient.models import Patient

register = template.Library()



PATIENT_GENDERS = dict(Patient.GENDER_CHOICES)


@register.filter
def get_gender_display(value):
    return PATIENT_GENDERS.get(value, value)
