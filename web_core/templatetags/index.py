from django import template

register = template.Library()


@register.filter
def index(indexable, i):
    return indexable[i]

@register.filter
def first_group_name(user):
    groups = user.groups.all()
    if groups:
        return groups[0].name
    return ''