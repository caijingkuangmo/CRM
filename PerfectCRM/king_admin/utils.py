#! /usr/bin/env python
# -*- coding:utf-8 -*-
__author__ = "laoliu"
from django.db.models import Q

def table_filter(request,admin_class):
    '''
    进行条件过滤并返回过滤后的数据
    :param request: 
    :param admin_class: 
    :return: 
    '''
    filter_conditions = {}
    filter_list = ['page','o','_q']
    for k,v in request.GET.items():
        if k in filter_list:  #分页和排序参数,搜索参数，不做为过滤条件，排除掉
            continue
        if v:
            filter_conditions[k] = v

    return admin_class.model.objects.filter(**filter_conditions).order_by(
        '-%s'%admin_class.ordering if admin_class.ordering else '-id'
    ),filter_conditions

def table_sort(request,objs):
    orderby_key = request.GET.get('o')
    if orderby_key:
        res = objs.order_by(orderby_key)
        if orderby_key.startswith('-'):
            orderby_key = orderby_key.strip('-')
        else:
            orderby_key = '-%s'%orderby_key
    else:
        res = objs
    return res,orderby_key


def table_search(request,admin_class,objs):
    search_key = request.GET.get('_q','')
    q_obj = Q()
    q_obj.connector = 'OR'
    for filed in admin_class.search_fields:
        q_obj.children.append(('%s__contains'%filed,search_key))

    objs = objs.filter(q_obj)
    return objs













