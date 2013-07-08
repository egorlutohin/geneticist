# coding: utf8
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm as UserCreationBaseForm
from django.contrib.auth.forms import UserCreationForm as UserChangeBaseForm
from django.contrib.auth.forms import ReadOnlyPasswordHashField
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


class UserChangeForm(forms.ModelForm):
    username = forms.RegexField(
        label=_("Username"), max_length=30, regex=r"^[\w.@+-]+$",
        help_text=_("Required. 30 characters or fewer. Letters, digits and "
                      "@/./+/-/_ only."),
        error_messages={
            'invalid': _("This value may contain only letters, numbers and "
                         "@/./+/-/_ characters.")})
    password = ReadOnlyPasswordHashField(label=_("Password"),
        help_text=_("Raw passwords are not stored, so there is no way to see "
                    "this user's password, but you can change the password "
                    "using <a href=\"password/\">this form</a>."))
    
    class Meta:
        model = user_model
        fields = ['username', 'last_name', 'first_name', 'patronymic',
                  'email', 'mo', 'password', 'is_active', 'is_staff',
                  'is_superuser', 'groups', 'user_permissions',
                  'last_login', 'date_joined']

    def __init__(self, *args, **kwargs):
        super(UserChangeForm, self).__init__(*args, **kwargs)
        f = self.fields.get('user_permissions', None)
        if f is not None:
            f.queryset = f.queryset.select_related('content_type')

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial["password"]
