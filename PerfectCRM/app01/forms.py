#! /usr/bin/env python
# -*- coding:utf-8 -*-
__author__ = "laoliu"

from django.forms import ModelForm
from app01 import models

class CustomerForm(ModelForm):

    def __new__(cls,*args,**kwargs):
        #form表单前端自带样式觉得丑，就可以这么自己加上样式
        for field_name,field_obj in cls.base_fields.items():
            field_obj.widget.attrs['class'] = 'form-control'

            if field_name in cls.Meta.readonly_fields:
                field_obj.widget.attrs['disabled'] = 'disabled'

        return ModelForm.__new__(cls, *args, **kwargs)

    def clean_qq(self):
        print('cleam_qq',self.instance.qq,self.cleaned_data["qq"])
        if self.instance.qq != self.cleaned_data['qq']:
            self.add_error("qq",'傻逼你还尝试黑我')
        return self.cleaned_data['qq']

    class Meta:
        model = models.Customer
        fields = "__all__"
        exclude = ['tags','content','memo','status','referral_from','consult_course']  #把这些字段排除在外不显示
        readonly_fields = ['qq','consultant','source',]  #自定义哪些字段只读，信息不可修改


class EnrollmentForm(ModelForm):

    def __new__(cls,*args,**kwargs):
        print("base fields",cls.base_fields)
        #form表单前端自带样式觉得丑，就可以这么自己加上样式
        for field_name,field_obj in cls.base_fields.items():
            field_obj.widget.attrs['class'] = 'form-control'


        return ModelForm.__new__(cls,*args,**kwargs)

    class Meta:
        model = models.Enrollment
        fields = ['enrolled_class','consultant']


class PaymentForm(ModelForm):

    def __new__(cls,*args,**kwargs):
        print("base fields",cls.base_fields)
        #form表单前端自带样式觉得丑，就可以这么自己加上样式
        for field_name,field_obj in cls.base_fields.items():
            field_obj.widget.attrs['class'] = 'form-control'

        return ModelForm.__new__(cls,*args,**kwargs)

    class Meta:
        model = models.Payment
        fields = '__all__'



