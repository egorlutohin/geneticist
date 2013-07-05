from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm as UserCreationBaseForm
from django.contrib.auth.forms import UserCreationForm as UserChangeBaseForm
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.utils.translation import ugettext, ugettext_lazy as _


user_model = get_user_model()


class UserCreationForm(UserCreationBaseForm):
    class Meta:
        model = user_model
        fields = ("username",)

    def clean_username(self):
        username = self.cleaned_data["username"]
        try:
            user_model._default_manager.get(username=username)
        except user_model.DoesNotExist:
            return username
        raise forms.ValidationError(self.error_messages['duplicate_username'])


class UserChangeForm(UserChangeBaseForm):
    def __init__(self, *args, **kwargs):
        super(UserChangeBaseForm, self).__init__(*args, **kwargs)

    class Meta:
        model = user_model
