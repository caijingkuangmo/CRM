#! /usr/bin/env python
# -*- coding:utf-8 -*-
__author__ = "laoliu"

from django.shortcuts import HttpResponse,render,redirect
from app01.permissions import permission_list
from django.core.urlresolvers import resolve

def perm_check(*args,**kwargs):
    request = args[0]
    if request.user.is_authenticated():  #是否登录验证
        for permission_name, v in permission_list.perm_dic.items():
            print(permission_name, v)
            url_matched = False
            if v['url_type'] == 1:  #absolute
                if v['url'] == request.path:  #绝对url匹配上
                    url_matched = True
            else:
                #把绝对的url请求转成相对的url  name
                resolve_url_obj = resolve(request.path)
                print('resolve_url_obj',resolve_url_obj)
                if resolve_url_obj.url_name == v['url']:  #相对的url 别名匹配上
                    url_matched = True

                if url_matched:
                    print('url match...',permission_name)
                    if v['method'] == request.method:  #请求方法也匹配上
                        print('method match...',permission_name)
                        arg_matched = True
                        for request_arg in v['args']:
                            request_method_func = getattr(request,v['method'])
                            if not request_method_func.get(request_arg):
                                arg_matched = False

                        if arg_matched:  #走到这里，仅代表这个请求和这条权限定义的规则  匹配上了，还没区分用户有没有这权限
                            print('arg match...',permission_name)

                            #判断是否有钩子函数，有还要在这里执行

                            print(request.user)
                            print(request.user.has_perm(permission_name))
                            #这里进行判断  用户有没有这个权限
                            if request.user.has_perm(permission_name):
                                print("有权限",permission_name)
                                return True

    else:
        return redirect("/account/login/")




def check_permission(func):

    def inner(*args,**kwargs):
        print('--->args',args,kwargs)
        print('--->func',func)
        if perm_check(*args,**kwargs) is True:
            return func(*args,**kwargs)
        else:
            return HttpResponse('没权限')

    return inner