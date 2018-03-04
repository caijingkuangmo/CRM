#! /usr/bin/env python
# -*- coding:utf-8 -*-
__author__ = "laoliu"

from django.utils.translation import ugettext as _
from django.forms import ValidationError
from django.forms import forms,ModelForm

from app01 import models

class CustomerModelForm(ModelForm):
    class Meta:
        model = models.Customer
        fields = "__all__"


def create_model_form(request,admin_class):
    '''动态生成model_form'''

    def default_clean(self):
        '''给所有的form默认添加一个clean验证'''
        print('---running default clean',admin_class.readonly_fields)
        #self是指实例的form对象，修改数据时，给instance传了一个  数据对象

        print('self',self)
        print(hasattr(self,'instance'))
        try:
            print(getattr(self,'instance'))
            print('---obj instance', self.instance)
        except Exception as e:
            print('getattr error',e)


        #创建和修改时，如果表只读  抛出异常
        if admin_class.readonly_table:
            raise ValidationError(
                        _('Table is readonly,cannot be modified or added'),
                        code='invalid'
                    )

        error_list = []
        if self.instance.id:   #change operation
            for field in admin_class.readonly_fields:
                #只读字段  不可变，用数据库的值和前端的值进行对比
                field_val = getattr(self.instance,field)  # val in db
                # print('hasattr_field',field_val,type(field_val))
                # print(hasattr(field_val,'select_related'))

                #多对多分支form验证
                if hasattr(field_val,"select_related"):  #m2m
                    m2m_objs = getattr(field_val,"select_related")()
                    #前端数据格式为  [1,2,3]
                    m2m_vals = [i[0] for i in m2m_objs.values_list('id')]
                    set_m2m_vals = set(m2m_vals)
                    set_m2m_vals_from_frontend = set([i.id for i in self.cleaned_data.get(field)])
                    print('m2m',set_m2m_vals,set_m2m_vals_from_frontend)
                    if set_m2m_vals != set_m2m_vals_from_frontend:
                        # error_list.append(ValidationError(
                        #
                        #     _("Field %(field)s is readonly"),
                        #     code="invalid",
                        #     params={"field":field},
                        # ))
                        self.add_error(field,'field is readonly')

                    continue

                #前端获取到的值  封装在clean_data里
                # print('cleaned data',self.cleaned_data)
                field_val_from_frontend = self.cleaned_data.get(field)
                print('---field compare',field,field_val,field_val_from_frontend)
                if field_val_from_frontend != field_val:

                    #django也有对这个抛出异常有解释的，其中抛出单个和多个错误
                    error_list.append(ValidationError(
                        _('Field %(field)s is readonly,data should be %(val)s'),
                        code='invalid',
                        params={'field':field,'val':field_val},
                    ))

        #invoke user's cutomized form validation
        #扩展调用
        self.ValidationError = ValidationError
        respone = admin_class.default_form_validation(self)
        if respone:
            error_list.append(respone)

        if error_list:
            raise ValidationError(error_list)





    def __new__(cls,*args,**kwargs):
        #super(CustomerForm,self).__new__(*args,**kwargs)
        print("base fields",cls.base_fields)
        #form表单前端自带样式觉得丑，就可以这么自己加上样式
        for field_name,field_obj in cls.base_fields.items():
            field_obj.widget.attrs['class'] = 'form-control'

            if not hasattr(admin_class,"is_add_form"):  #代表这里添加form，不需要disabled
                #循环只读字段  给其加上 不可编辑
                if field_name in admin_class.readonly_fields:
                    field_obj.widget.attrs['disabled'] = 'disabled'

            #循环字段时，去admin里找下有没有单字段验证方法，有就给form对象加上
            if hasattr(admin_class,'clean_%s'%field_name):
                field_clean_func = getattr(admin_class,"clean_%s"%field_name)
                setattr(cls,"clean_%s"%field_name,field_clean_func)

        return ModelForm.__new__(cls,*args,**kwargs)

    class Meta:
        model = admin_class.model
        fields = "__all__"
        exclude = admin_class.modelform_exclude_fields  #排除哪些字段在前端不被form渲染

    attrs = {'Meta':Meta,
             '__new__':__new__,
             'clean':default_clean}
    _model_form_class = type('DynamicModelForm',(ModelForm,),attrs)
    # setattr(_model_form_class,'__new__',__new__)

    return _model_form_class