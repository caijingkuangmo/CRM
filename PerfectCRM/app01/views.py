# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render,HttpResponse,redirect
from app01 import models
from app01 import forms
from django.db import IntegrityError
import string,random,os
from PerfectCRM import settings
from django.core.cache import cache

# Create your views here.

def index(req):
    return render(req,'index.html')

def customer_list(req):
    print(req.user)
    print(req.user.userprofile.roles.all)
    # print(req.user.userprofile.roles.all)
    return render(req,'sales/customers.html')

def enrollment(req,customer_id):
    customer_obj = models.Customer.objects.get(id=customer_id)

    msgs = {}
    #post 下一步
    if req.method == "POST":
        enroll_form = forms.EnrollmentForm(req.POST)
        if enroll_form.is_valid():
            msg =  '''请将此链接发送给客户进行填写
            http://localhost:9999/crm/customer/registration/{enroll_obj_id}/{random_str}'''
            try:
                print("cleandata",enroll_form.cleaned_data)
                enroll_form.cleaned_data["customer"] = customer_obj
                enroll_obj = models.Enrollment.objects.create(**enroll_form.cleaned_data)
                print("enroll_obj ",enroll_obj)
                msgs["msg"] = '''请将此链接发送给客户进行填写
                http://localhost:9999/crm/customer/registration/{enroll_obj_id}/{random_str}'''
                random_str = "".join(random.sample(string.ascii_lowercase+string.digits,8))
                cache.set(enroll_obj.id, random_str, 3000)
                msgs["msg"] = msg.format(enroll_obj_id=enroll_obj.id,random_str=random_str)
            except IntegrityError as e:
                enroll_obj = models.Enrollment.objects.get(customer_id=customer_obj.id,
                                                           enrolled_class_id=enroll_form.cleaned_data['enrolled_class'].id)

                if enroll_obj.contract_agreed is True:  #从销售看，如果客户已经提交信息同意合同，点击下一步就是跳转到缴费页面
                    return redirect("/crm/contract_review/%s/"%enroll_obj.id)
                enroll_form.add_error('__all__','该用户的此条报名信息已存在，不能重复创建')
                random_str = "".join(random.sample(string.ascii_lowercase + string.digits, 8))
                cache.set(enroll_obj.id, random_str, 3000)

                msgs["msg"] =  msg.format(enroll_obj_id=enroll_obj.id,random_str=random_str)

    else:
        enroll_form = forms.EnrollmentForm()

    return render(req,"sales/enrollment.html",{'enroll_form':enroll_form,
                                               'customer_obj':customer_obj,
                                               'msgs':msgs})

def stu_registration(req,enroll_id,random_str):
    print(cache.get(enroll_id),random_str)
    if cache.get(enroll_id) == random_str:
        enroll_obj = models.Enrollment.objects.get(id=enroll_id)
        customer_form = forms.CustomerForm(instance=enroll_obj.customer)
        status = 0  #前端依据这个状态来判断是否要显示  内容填写框
        if req.method == "POST":
            #ajax 上传文件
            if req.is_ajax():
                print("ajax post",req.FILES)
                enroll_data_dir = "%s/%s"%(settings.ENROLLED_DATA,enroll_id)
                if not os.path.exists(enroll_data_dir):
                    # os.makedirs(enroll_data_dir,exist_ok=True)   python3
                    os.makedirs(enroll_data_dir)
                for k,file_obj in req.FILES.items():
                    with open("%s/%s"%(enroll_data_dir,file_obj.name),'wb') as f:
                        for chunk in file_obj.chunks():
                            f.write(chunk)
                return HttpResponse('success')

            customer_form = forms.CustomerForm(req.POST,instance=enroll_obj.customer)
            if customer_form.is_valid():
                customer_form.save()
                enroll_obj.contract_agreed = True  #同意合同
                enroll_obj.save()
                status = 1
                return render(req,"sales/stu_registration.html",{"status":status})
        else:
            #如果是客户已经在这个页面提交过信息，那下次访问，就不在是填了，而是要显示提交成功的信息
            if enroll_obj.contract_agreed == True:
                status = 1
        return render(req,'sales/stu_registration.html',{'customer_form':customer_form,
                                                         'enroll_obj':enroll_obj,
                                                         'status':status})
    else:
        return HttpResponse('去你个傻逼，还想黑我')


def contract_review(req,enroll_id):
    enroll_obj = models.Enrollment.objects.get(id=enroll_id)
    enroll_form = forms.EnrollmentForm(instance=enroll_obj)
    customer_form = forms.CustomerForm(instance=enroll_obj.customer)
    return render(req,'sales/contract_review.html',{'enroll_obj':enroll_obj,
                                      'customer_form':customer_form,
                                      'enroll_form':enroll_form})


def enrollment_rejection(req,enroll_id):
    enroll_obj = models.Enrollment.objects.get(id=enroll_id)
    enroll_obj.contract_agreed = False
    enroll_obj.save()

    #合同驳回后  跳转到 销售点击报名  进入的url  在这里会生成 客户填写信息 的url

    return redirect("/crm/customer/%s/enrollment/"%enroll_obj.customer.id)


def payment(req,enroll_id):
    enroll_obj = models.Enrollment.objects.get(id=enroll_id)

    errors = []
    if req.method == "POST":
        payment_amount = req.POST.get('amount')
        if payment_amount:
            payment_amount = int(payment_amount)
            if payment_amount < 500:
                errors.append("缴费金额低于了500")
            else:
                payment_obj = models.Payment.objects.create(
                    customer = enroll_obj.customer,
                    course = enroll_obj.enrolled_class.course,
                    amount = payment_amount,
                    consultant = enroll_obj.consultant
                )

                enroll_obj.contract_approved = True  #审核过合同
                enroll_obj.save()

                #修改报名状态
                enroll_obj.customer.status = 1
                enroll_obj.customer.save()

                #跳转到客户库
                return redirect('/king_admin/app01/customer/')

        else:
            errors.append('必要输入金额')

    return render(req,"sales/payment.html",{'enroll_obj':enroll_obj,
                                            'errors':errors})

