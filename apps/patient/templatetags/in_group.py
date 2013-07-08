from django.contrib.auth import get_user_model
from django import template
from django.utils.encoding import force_unicode

from django import forms


register=template.Library()


User = get_user_model()


@register.filter
def in_group(user, groups):
    """Returns a boolean if the user is in the given group, or comma-separated
    list of groups.

    Usage::

        {% if user|in_group:"Friends" %}
        ...
        {% endif %}

    or::

        {% if user|in_group:"Friends,Enemies" %}
        ...
        {% endif %}

    """
    if user is None:
        return False
    group_list = force_unicode(groups).split(',')
    return User.objects.filter(groups__name__in=group_list,
                               username=user.username) \
                       .exists()

@register.filter                       
def date_fields_id(form):
    l = []
    for field in form:
        if isinstance(field.field, forms.DateField):
            l.append('#' + field.auto_id)
    
    return ', '.join(l)

@register.filter                       
def no_date_fields_id(form):
    l = []
    for field in form:
        if not isinstance(field.field, forms.DateField):
            l.append('#' + field.auto_id)
            
    return ', '.join(l)

