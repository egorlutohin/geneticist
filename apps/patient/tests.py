#coding: utf8
from datetime import date

from django.core.urlresolvers import reverse
from django_webtest import WebTest

from organization.models import Organization
from patient.models import Patient


class PatientCases(WebTest):
    def setUp(self):
        self.organization = Organization.objects.create(code=u'123',
                                                        name=u'ГКБ ЧП',
                                                        full_name=u'Картошка')

    def get_base_info(self):
        return {'first_name': u'Иван',
                'last_name': u'Иванов',
                'patronymic': u'Иванович',
                'birthday': date(2005, 5, 25),
                'death': date(2006, 6, 6),
                'seria_policy': '5005',
                'number_policy': '654789',
                'code_insurance_company': '454',
                'registration': u'650321 г. Томск, ул. Кротова 7 кв 41',
                'residence': u'658965 г. Барнаул, ул Мира 12',
                'allocate_lpu': self.organization.pk,
                'comment': u'Некий комментарий к базе данных',
                'social_status': Patient.SOCIAL_STATUSES[0][1][0][0],
                'special_cure': Patient.SPECIAL_CURES[0][0],
                'type': Patient.TYPE_CHOICES[0][0],
                'gender': Patient.GENDER_CHOICES[0][0],
                'diagnosis-TOTAL_FORMS': 1,
                'diagnosis-INITIAL_FORMS': 1,
                'diagnosis-MAX_NUM_FORMS': 1,
                'diagnosis-0-code': u'A35.0.1',
                'diagnosis-0-name': u'Болячка',
                'visit-code': u'ГРУ МО',
                'visit-name': u'Обл. больница',
                }

    def update_csrf(self, form):
        param_name = 'csrfmiddlewaretoken'
        form[param_name] = form.fields[param_name][0].value

    def create_patient(self):
        form = self.app.get(reverse('patient_add')).form
        for name, value in self.get_base_info().iteritems():
            form[name] = value
        self.update_csrf(form)
        response = form.submit()
        self.assertEqual(Patient.objects.count(), 1)
        patient = Patient.objects.all()[0]
        self.assertIsNotNone(patient.diagnosis_text)
        self.assertGreater(len(patient.diagnosis_text), 0)
        visit = patient.visit_set.all()[0]
        self.assertEqual(visit.is_add, True)
        return patient

    def test_create_patient(self):
        patient = self.create_patient()
        self.assertEqual(patient.code_allocate_lpu, self.organization.code)
        self.assertEqual(patient.name_allocate_lpu, self.organization.full_name)

    def test_edit_patient(self):
        patient = self.create_patient()
        url_edit = reverse('patient_edit', kwargs={'patient_id': patient.pk})
        form = self.app.get(url_edit).form
        form['diagnosis-1-name'] = ''
        form.submit()
        self.assertEqual(patient.diagnosis_set.count(), 1)

        form['diagnosis-1-name'] = u'Блихи'
        form['diagnosis-1-code'] = u'B34.12'
        form.submit()
        self.assertEqual(patient.diagnosis_set.count(), 2)

        form = self.app.get(url_edit).form
        form['diagnosis-1-DELETE'] = u'on'
        form.submit()
        self.assertEqual(patient.diagnosis_set.active().count(), 1)
