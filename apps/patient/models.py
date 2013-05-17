#coding: utf8
from django.db import Models
from django.db.models.query import QuerySet


class BaseQuerySet(QuerySet):
    def delete(self):
        self.update(is_active=False)

    def delete_real(self):
        super(BaseQuerySet, self).delete()

    def active(self):
        return self.filter(is_active=True)


class BaseManager(models.Manager):
    def get_query_set(self):
        return BaseQuerySet(self.model, using=self._db)

    def active(self):
        return self.filter(is_active=True)


class BaseModel(models.Model):
    class Meta:
        abstract = True
        ordering = ('name',)

    is_active = models.BooleanField("активный", default=True)

    objects = BaseManager()
    all_objects = models.Manager()

    def delete(self, *args, **kwargs):
        self.is_active = False
        self.save()


class Patient(BaseModel):
    first_name = models.CharField(u'Имя', max_length=100, db_index=True)
    last_name = models.CharField(u'Фамилия', max_length=100, db_index=True)
    patronymic = models.CharField(u'Отчество', max_length=100, db_index=True)
    birthday = models.DateField(verbose_name=u'Дата рождения',
                                blank=True, null=True)
    death = models.DateField(verbose_name=u'Дата смерти',
                             blank=True, null=True)
    seria_policy = models.CharField(u'Серия страхового полиса',
                                    max_length=20, blank=True, null=True)
    number_policy = models.CharField(u'Номер страхового полиса',
                                     max_length=10, blank=True, null=True)
    code_insurance_company = models.CharField(u'Код страховой компании',
                                              max_length=30,
                                              blank=True, null=True)
    registration = models.TextField(verbose_name=u'Адрес регистрации',
                                    blank=True, null=True)
    residence = models.TextField(verbose_name=u'Адрес проживания',
                                 blank=True, null=True)
    comment = models.TextField(verbose_name=u'Комментарий к диагнозу',
                               blank=True, null=True)
    social_status = models.IntegerField(verbose_name=u'Социальный статус')  # TODO: нужно выяснить о статусах


class Diagnosis(BaseModel):
    """ Диагноз пациента """
    patient = models.ForeignKey(Patient)
    code = models.CharField(u'Код диагноза по МКБ-10',
                                      max_length=10)
    name = models.TextField(verbose_name=u'Название диагноза')

    def __unicode__(self):
        return u"%s (%s)" % (self.name, self.code,)

    class Meta:
        verbose_name = u'Диагноз пациента'
        verbose_name_plural = u'Диагнозы пациента'
