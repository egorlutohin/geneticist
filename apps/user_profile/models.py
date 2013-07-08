# coding: utf8
from django.db import models
from django.contrib.auth.models import AbstractUser

from organization.models import Organization


class CustomUser(AbstractUser):
    patronymic = models.CharField(u'Отчество', max_length=30, blank=True)
    mo = models.ForeignKey(Organization,
                           verbose_name=u'Мед. организация',
                           blank=True, null=True)
    mo_name = models.TextField(verbose_name=u'Название мед. организации')

    def __unicode__(self):
        return super(CustomUser, self).__unicode__()

    def save(self, *args, **kwargs):
        if self.mo:
            self.mo_name = self.mo.name
        super(CustomUser, self).save(*args, **kwargs)

    class Meta:
        verbose_name = u'Профиль сотрудника'
        verbose_name_plural = u'Профили сотрудников'
        db_table = 'auth_user'
