from django.contrib.auth.models import User
from django import template
from django.utils.encoding import force_unicode


register=template.Library()


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
