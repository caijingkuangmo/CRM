# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from king_admin.utils import table_filter,table_sort,table_search
from django.shortcuts import render,redirect
from king_admin import kingadmin
from king_admin.forms import create_model_form
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required
# Create your views here.

@login_required
def index(req):
    print(kingadmin.enabled_admins)
    return render(req,'king_admin/index.html',{'table_list':kingadmin.enabled_admins})
@login_required
def display_table_objs(req,app_name,table_name):
    print('-->',app_name,table_name)
    print(type(app_name),type(table_name))
    print(kingadmin.enabled_admins)
    #admin_class  根据这个类，获取显示条件  还操作.model下的数据
    admin_class = kingadmin.enabled_admins[app_name][table_name]

    #action  post请求
    print(req.method)
    if req.method == "POST":
        print(req.POST)
        selected_ids = req.POST.get('selected_ids')
        action = req.POST.get('action')
        if selected_ids:
            selected_objs = admin_class.model.objects.filter(id__in=selected_ids.split(','))
        else:
            raise KeyError('No object selected.')

        if hasattr(admin_class,action):
            action_func = getattr(admin_class,action)
            req._admin_action = action
            return action_func(admin_class(),req,selected_objs)

    # object_list = admin_class.model.objects.all()
    object_list,filter_condtions = table_filter(req,admin_class)  #过滤数据

    object_list = table_search(req,admin_class,object_list)  #搜索查询

    object_list,order_key = table_sort(req, object_list)  #排序数据
    paginator = Paginator(object_list, admin_class.list_per_page) # Show 25 contacts per page

    page = req.GET.get('page')
    try:
        query_sets = paginator.page(page)
    except PageNotAnInteger:
        query_sets = paginator.page(1)
    except EmptyPage:
        query_sets = paginator.page(paginator.num_pages)

    print('enter filter')
    return render(req,'king_admin/table_objs.html',{'admin_class':admin_class,
                                                    'query_sets': query_sets,
                                                    'filter_condtions':filter_condtions,
                                                    'order_key':order_key,
                                                    'previous_order_key':req.GET.get('o',''),
                                                    'search_text':req.GET.get('_q','')})

@login_required
def table_obj_change(req,app_name,table_name,obj_id):
    admin_class = kingadmin.enabled_admins[app_name][table_name]
    model_form_class = create_model_form(req,admin_class)

    obj = admin_class.model.objects.get(id=obj_id)
    if req.method == "POST":
        #此时提交过来的post请求是修改数据，为了让前端通过form显示修改后的数据，可以直接把post数据传给form
        #如果不给instance赋值，是创建，给了，才是修改
        form_obj = model_form_class(req.POST,instance=obj)  #更新
        if form_obj.is_valid():
            form_obj.save()
    else:
        form_obj = model_form_class(instance=obj)
    return render(req,'king_admin/table_obj_change.html',{'form_obj':form_obj,
                                                          'admin_class':admin_class,
                                                          'app_name':app_name,
                                                          'table_name':table_name})

@login_required
def obj_delete(req,app_name,table_name,obj_id):
    admin_class = kingadmin.enabled_admins[app_name][table_name]
    obj = admin_class.model.objects.get(id=obj_id)

    errors = {}
    # 表只读 不能删除  直接报错
    if admin_class.readonly_table:
        errors = {'readonly_table': "table is readonly,obj {%s} cannot be deleted" % obj}

    if req.method == 'POST':
        if not admin_class.readonly_table:
            obj.delete()
            return redirect('/king_admin/%s/%s/'%(app_name,table_name))

    return render(req,'king_admin/table_obj_delete.html',{'admin_class':admin_class,
                                                          'objs':obj,
                                                          'app_name':app_name,
                                                          'table_name':table_name,
                                                          'errors':errors})



@login_required
def table_obj_add(req,app_name,table_name):
    admin_class = kingadmin.enabled_admins[app_name][table_name]
    admin_class.is_add_form = True
    model_form_class = create_model_form(req,admin_class)

    if req.method == "POST":
        #添加
        print('add  post data',req.POST)
        form_obj = model_form_class(req.POST)
        if form_obj.is_valid():
            form_obj.save()
            return redirect(req.path.replace('/add/','/'))
    else:
        form_obj = model_form_class()
    print('end views')
    return render(req,'king_admin/table_obj_add.html',{'form_obj':form_obj,
                                                       'admin_class':admin_class})

@login_required
def password_reset(req,app_name,table_name,obj_id):
    admin_class = kingadmin.enabled_admins[app_name][table_name]
    model_form_class = create_model_form(req,admin_class)
    obj = admin_class.model.objects.get(id=obj_id)

    errors = {}
    if req.method == "POST":
        _password1 = req.POST.get('password1')
        _password2 = req.POST.get('password2')

        print(_password1,_password2)
        if _password1 == _password2:
            if len(_password1) > 5:
                obj.set_password(_password1)
                obj.save()
                return redirect(req.path.rstrip('password/'))
            else:
                errors["password_too_short"] = "must not less than 6 letters"
        else:
            errors['invalid_password'] = 'passowrds are not the same'
    return render(req,'king_admin/password_reset.html',{'obj':obj,
                                                        'errors':errors})