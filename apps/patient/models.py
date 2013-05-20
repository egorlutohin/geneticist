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
    SOCIAL_STATUSES = (
        u'Дошкольник', (
            (1, u'Дошкольник, оставшийся без попечения родителей',),
            (2, u'Дошкольник-сирота',),
        ),
        u'Школьник', (
            (3, u'Школьник, оставшийся без попечения родителей',),
            (4, u'Школьник-сирота',),
        ),
        u'Студент (аспирант)', (
            (5, u'Студент (аспирант), оставшийся без попечения родителей',),
            (6, u'Студент (аспирант)-сирота',),
        ),
        (7, u'Работающий',),
        (8, u'Неработающий',),
        (9, u'Пенсионер',),
        (10, u'Военнослужащий',),
    )
    SPECIAL_CURES = ((1, u'Нуждается',),
                     (2, u'Не нуждается'),
                     (3, u'Получает',),
                     (4, u'Снят',),
                     (5, u'Не нуждается',),)
    TYPES_RESIDENCE = ((1, u'Житель г. Новосибирска',),
                       (2, u'Житель НСО',),
                       (3, u'Житель Инобластной',),)
    TYPE_CHOICES = ((1, u'Пробант',)
                    (2, u'Плод'),)
    SEX_CHOICES = ((1, u'М',),
                   (2, u'Ж',),
                   (3, u'Интерсекс',),)
    first_name = models.CharField(u'Имя', max_length=100, db_index=True)
    last_name = models.CharField(u'Фамилия', max_length=100, db_index=True)
    patronymic = models.CharField(u'Отчество', max_length=100, db_index=True)
    birthday = models.DateField(verbose_name=u'Дата рождения',
                                blank=True, null=True, db_index=True)
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
    social_status = models.IntegerField(verbose_name=u'Социальный статус',
                                        blank=True, null=True,
                                        choices=SOCIAL_STATUSES)
    special_cure = models.IntegerField(verbose_name=u'Специальное лечение',
                                       default=SPECIAL_CURES[4][0],
                                       choices=SPECIAL_CURES)
    type = models.IntegerField(verbose_name=u'Тип пациента',
                               choices=TYPE_CHOICES)
    sex = models.IntegerField(verbose_name=u'Пол', choices=SEX_CHOICES)
    date_registration = models.DateField(default=date.today,
                                         verbose_name=u'Дата постановки на учет')
    date_created = models.DateTimeField(default=datetime.now,
                                        verbose_name=u'Дата заполнения анкеты')

    def __unicode__(self):
        params = (self.first_name, self.last_name, self.patronymic,)
        return u'%s %s %s' % params

    class Meta:
        verbose_name = u'Пациент'
        verbose_name_plural = u'Пациенты'
        ordering = ['first_name', 'last_name', 'patronymic', 'birthday']


class Visit(BaseModel):
    """ Посещение пациентом генетика """
    patient = models.ForeignKey(Patient)
    is_add = models.BooleanField(
        verbose_name=u'Первое посещение (внесение в регистр)',
        default=False, db_index=True
    )
    code = models.CharField(u'Код МО', max_length=80)
    name = models.CharField(u'Наименование МО', max_length=100)
    date_created = models.DateTimeField(
        default=datetime.now,
        verbose_name=u'Дата внесения в регистр/Дата посещения'
    )

    class Meta:
        verbose_name = u'Посещение пациентом',
        verbose_name_plural = u'Посещения пациентом'
        ordering = ['is_add', 'date_created']



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
        ordering = [u'code']
