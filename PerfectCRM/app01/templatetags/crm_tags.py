#! /usr/bin/env python
# -*- coding:utf-8 -*-
__author__ = "laoliu"

from django import template
# from django.core.exceptions import FieldDoesNotExist
from django.utils.safestring import mark_safe


register = template.Library()

@register.simple_tag
def render_enroll_contract(enroll_obj):
    course_name = enroll_obj.enrolled_class
    return enroll_obj.enrolled_class.contract.template.format(course_name=course_name)

