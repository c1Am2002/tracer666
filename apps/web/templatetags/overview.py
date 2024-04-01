from django.template import Library
from django.urls import reverse
from apps.web import models

register = Library()


@register.simple_tag
def user_space(size):
    """将使用空间格式转换"""
    if size >= 1024 * 1024 * 1024:
        return "%.2f GB" % (size / (1024 * 1024 * 1024),)
    elif size >= 1024 * 1024:
        return "%.2f MB" % (size / (1024 * 1024),)
    elif size >= 1024:
        return "%.2f KB" % (size / 1024,)
    else:
        return "%d B" % size