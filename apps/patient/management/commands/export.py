#coding: utf8
import pyExcelerator
from django.core.management.base import BaseCommand, CommandError

from common_helpers import nested_commit_on_success
from patient.models import Visit, Patient, Diagnosis


class Command(BaseCommand):
    help = u"Export from patients.xls into database https://github.com/dicos/geneticist/issues/47"

    @nested_commit_on_success
    def handle(self, *args, **options):
        book = pyExcelerator.parse_xls("patients.xls")
        patient_info = book[0]
        diagnosis_info = book[1]
