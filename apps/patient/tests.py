#coding: utf8
from django_webtest import WebTest


class PatientCases(WebTest):
    def test_create_patient(self):
        form = self.app.get(reverse('patient_data')).form
