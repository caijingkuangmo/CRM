# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render,redirect
from django.contrib.auth import login,authenticate,logout

# Create your views here.

def acc_login(req):
    errors = {}
    if req.method == "POST":
        _email = req.POST.get('email')
        _password = req.POST.get('password')

        user = authenticate(username=_email,password=_password)
        print('auth res',user)  #成功返回用户对象   失败返回none

        if user:
            login(req,user)  #不仅做登录验证，还是写入session
            next_url = req.GET.get('next','/')  #发送post请求时，同时可以发送get请求
            return redirect("/")
        else:
            errors['error'] = "Wrong username or password!"
    return render(req,'login.html',{"errors":errors})


def acc_logout(req):
    logout(req)
    return redirect('/account/login/')


def index(req):

    return render(req,'index.html')

