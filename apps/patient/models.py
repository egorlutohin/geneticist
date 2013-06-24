#coding: utf8
from datetime import date, datetime

from django.db import models
from django.db.models.query import QuerySet
from django_history.models import FullHistoricalRecords
from django_history.current_context import CurrentUserField

from organization.models import Organization


class BaseQuerySet(QuerySet):
    def delete(self):
        self.update(is_active=False)

    def delete_real(self):
        super(BaseQuerySet, self).delete()

    def active(self):
        return self.filter(is_active=True)


class BaseManager(models.Manager):
    def get_query_set(self):
        return BaseQuerySet(self.model, using=self._db).active()

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
    SOCIAL_STATUSES = (
        (u'Дошкольник', (
                (1, u'Дошкольник, оставшийся без попечения родителей',),
                (2, u'Дошкольник-сирота',),
            ),
        ),
        (u'Школьник', (
                (3, u'Школьник, оставшийся без попечения родителей',),
                (4, u'Школьник-сирота',),
            ),
        ),
        (u'Студент (аспирант)', (
                (5, u'Студент (аспирант), оставшийся без попечения родителей',),
                (6, u'Студент (аспирант)-сирота',),
            ),
        ),
        (7, u'Работающий',),
        (8, u'Неработающий',),
        (9, u'Пенсионер',),
        (10, u'Военнослужащий',)
    )

    NEED_CURE = 1
    NOT_NEED_CURE = 2
    GET_CURE = 3
    RAISE_CURE = 4
    SPECIAL_CURES = ((NEED_CURE, u'Нуждается',),
                     (NOT_NEED_CURE, u'Не нуждается'),
                     (GET_CURE, u'Получает',),
                     (RAISE_CURE, u'Снят',),)
    TYPE_RESIDENCES = ((1, u'Житель г. Новосибирска',),
                       (2, u'Житель НСО',),
                       (3, u'Житель Инобластной',),)
    TYPE_CHOICES = ((1, u'Пробант',),
                    (2, u'Плод'),)
    GENDER_CHOICES = ((1, u'М',),
                      (2, u'Ж',),
                      (3, u'Интерсекс',),
                      (4, u'Неизвестно',),)
    first_name = models.CharField(u'Имя', max_length=100)
    last_name = models.CharField(u'Фамилия', max_length=100)
    patronymic = models.CharField(u'Отчество', max_length=100)
    full_name = models.CharField(u'Полное имя', max_length=300,
                                 db_index=True, editable=False,
                                 blank=True, default='')
    prev_full_name = models.CharField(u'Предыдущее олное имя',
                                      max_length=300, editable=False,
                                      blank=True, default='')
    all_full_names = models.TextField(verbose_name=u'Все ФИО',
                                      blank=True, db_index=True)
    birthday = models.DateField(verbose_name=u'Дата рождения',
                                blank=True, null=True, db_index=True)
    death = models.DateField(verbose_name=u'Дата смерти',
                             blank=True, null=True, db_index=True)
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
    code_allocate_lpu = models.CharField(u'Код МО прикрепления',
                                         max_length=20, blank=True, null=True)
    name_allocate_lpu = models.TextField(u'Название МО прикрепления',
                                         max_length=100, blank=True, null=True)
    allocate_lpu = models.ForeignKey(Organization, blank=True, null=True,
                                     verbose_name=u'ЛПУ прикрепления')
    _diagnosis_help = u'Вспомогательное поле, нужно для вывода диагноза в поиске'
    diagnosis_text = models.TextField(verbose_name=u'Диагноз по МКБ-10',
                                      editable=False, blank=True, null=True,
                                      help_text=_diagnosis_help)
    diagnosis_text_code = models.TextField(verbose_name=u'Диагноз по МКБ-10',
                                           editable=False, blank=True, null=True,
                                           help_text=_diagnosis_help)
    diagnosis_comment = models.TextField(verbose_name=u'Комментарий к диагнозу',
                                         blank=True, null=True)
    social_status = models.IntegerField(verbose_name=u'Социальный статус',
                                        blank=True, null=True, db_index=True,
                                        choices=SOCIAL_STATUSES)
    special_cure = models.IntegerField(verbose_name=u'Специальное лечение',
                                       default=NOT_NEED_CURE,
                                       choices=SPECIAL_CURES,
                                       db_index=True)
    type_residence = models.IntegerField(verbose_name=u"Пациент",
                                         choices=TYPE_RESIDENCES,
                                         default=TYPE_RESIDENCES[0][0],
                                         db_index=True)
    type = models.IntegerField(verbose_name=u'Тип пациента',
                               choices=TYPE_CHOICES)
    gender = models.IntegerField(verbose_name=u'Пол', choices=GENDER_CHOICES)
    comment = models.TextField(verbose_name=u'Комментарий',
                               blank=True, null=True)
    date_registration = models.DateField(default=date.today,
                                         verbose_name=u'Дата постановки на учет')
    date_created = models.DateTimeField(default=datetime.now,
                                        verbose_name=u'Дата заполнения анкеты',
                                        editable=False)
    user_changed = CurrentUserField()

    history = FullHistoricalRecords()

    def get_full_name(self):
        return ' '.join((self.last_name, self.first_name, self.patronymic,))

    def __unicode__(self):
        params = [self.full_name]
        if self.birthday:
            params.append(self.birthday.strftime('%d.%m.%Y'))
        return ' '.join(params)

    def save(self, *args, **kwargs):
        full_name = self.get_full_name()
        if full_name != self.full_name:
            self.prev_full_name = self.full_name
            self.full_name = full_name
            self.all_full_names = full_name + "\n" + self.all_full_names
        if not self.pk:
            self.all_full_names = full_name
        if self.allocate_lpu:
            self.code_allocate_lpu = self.allocate_lpu.code
            self.name_allocate_lpu = self.allocate_lpu.full_name
        else:
            self.code_allocate_lpu = self.name_allocate_lpu = ''
        super(Patient, self).save(*args, **kwargs)

    class Meta:
        verbose_name = u'Пациент'
        verbose_name_plural = u'Пациенты'
        ordering = ['first_name', 'last_name', 'patronymic', 'birthday']


class Visit(BaseModel):
    """ Посещение пациентом генетика """
    patient = models.ForeignKey(Patient)
    is_add = models.BooleanField(
        verbose_name=u'Первое посещение (внесение в регистр)',
        default=False, db_index=True, editable=False
    )
    code = models.CharField(u'Код МО', max_length=7)
    name = models.TextField(u'Наименование МО')
    lpu = models.ForeignKey(Organization, verbose_name=u'МО посещения')
    date_created = models.DateTimeField(
        default=datetime.now,
        verbose_name=u'Дата внесения в регистр/Дата посещения'
    )
    user_created = CurrentUserField(one_time=True)

    history = FullHistoricalRecords()

    def __unicode__(self):
        return "%s %s" % (self.name, self.date_created.strftime('%d.%m.%Y'))

    def save(self, *args, **kwargs):
        self.code = self.lpu.code
        self.name = self.lpu.name
        super(Visit, self).save(self, *args, **kwargs)

    class Meta:
        verbose_name = u'Посещение пациентом',
        verbose_name_plural = u'Посещения пациентом'
        ordering = ['pk']
        get_latest_by = 'pk'



class Diagnosis(BaseModel):
    """ Диагноз пациента """
    patient = models.ForeignKey(Patient)
    code = models.CharField(u'Код диагноза по МКБ-10',
                            max_length=10, db_index=True)
    name = models.TextField(verbose_name=u'Название диагноза',
                            db_index=True)
    user_changed = CurrentUserField()

    history = FullHistoricalRecords()

    def __unicode__(self):
        return u"%s (%s)" % (self.name, self.code,)

    class Meta:
        verbose_name = u'Диагноз пациента'
        verbose_name_plural = u'Диагнозы пациента'
        ordering = [u'code']
