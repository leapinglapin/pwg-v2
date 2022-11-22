from django import template

register = template.Library()


@register.filter
def is_entered_in(user, giveaway):
    if giveaway.entry_set.filter(user=user).exists():
        return True
    return False
