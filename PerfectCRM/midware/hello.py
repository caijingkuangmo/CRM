#! /usr/bin/env python
# -*- coding:utf-8 -*-
__author__ = "laoliu"


from django.utils.deprecation import MiddlewareMixin

class testMiddleware(MiddlewareMixin):

    def process_request(self,request):
        print(11)
        print('================')
        print(request.method)
        print(request.GET)
        print(request.POST)
        print(request.path)
        print(request.COOKIES)

    def process_response(self,request,response):
        print(22)
        return response