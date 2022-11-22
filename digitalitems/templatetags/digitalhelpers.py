# Based on this: https://simpleisbetterthancomplex.com/snippet/2016/08/22/dealing-with-querystring-parameters.html
# and this: https://gist.github.com/benbacardi/d6cd0fb8c85e1547c3c60f95f5b2d5e1
import datetime

from django import template

register = template.Library()


@register.filter
def get_metadata_from_folder(folder):
    return folder['metadata']
