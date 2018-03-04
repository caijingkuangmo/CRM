#! /usr/bin/env python
# -*- coding:utf-8 -*-
__author__ = "laoliu"

#url type : 0 = related   1 = absolute

perm_dic = {
    'app01.can_access_my_course':{
        'url_type' : 0,
        'url' : 'stu_my_classes',
        'method' : 'GET',
        'args' : [],
        # 'hooks' : ['func1' and 'func2'],  #业务逻辑处理函数
    },

    'app01.can_access_customer_list': {
        'url_type': 1,
        'url': '/king_admin/app01/customer/',  #绝对路径  支持正则
        'method': 'GET',
        'args': []
    },

    'app01.can_access_customer_detail': {
        'url_type': 0,
        'url': 'table_obj_change',
        'method': 'GET',
        'args': []
    },

    'app01.can_access_homework_detail': {
        'url_type': 0,
        'url': 'homework_detail',
        'method': 'GET',
        'args': []
    },

    'app01.can_upload_homework': {
        'url_type': 0,
        'url': 'table_obj_change',
        'method': 'POST',
        'args': []
    },
}