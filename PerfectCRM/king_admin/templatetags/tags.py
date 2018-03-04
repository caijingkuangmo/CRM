#! /usr/bin/env python
# -*- coding:utf-8 -*-
__author__ = "laoliu"

from django import template
from django.core.exceptions import FieldDoesNotExist
from django.utils.safestring import mark_safe
from django.utils.timezone import datetime,timedelta

register = template.Library()


@register.simple_tag
def render_table_name(admin_class):
    return admin_class.model._meta.verbose_name_plural

@register.simple_tag
def get_query_sets(admin_class):
    return admin_class.model.objects.all()

@register.simple_tag
def build_table_row(obj,admin_class,request):
    row_ele = ''
    for index,column in enumerate(admin_class.list_display):
        try:
            field_obj = obj._meta.get_field(column)

            if field_obj.choices:   #choices type
                column_data = getattr(obj,'get_%s_display'%column)()
            else:
                column_data = getattr(obj,column)

            if type(column_data).__name__ == 'datetime':
                column_data = column_data.strftime('%Y-%m-%d %H:%M:%S')

            if index == 0:  #让第一列的数据加a标签可点，以进入到数据修改页
                column_data = '''<a href="{request_path}{obj_id}/change/">{column_data}</a>'''.format(request_path=request.path,
                                                                                                        obj_id=obj.id,
                                                                                                    column_data=column_data)

        except FieldDoesNotExist as e:
            if hasattr(admin_class,column):
                column_func = getattr(admin_class,column)
                admin_class.instance = obj
                admin_class.request = request
                column_data = column_func()

        row_ele += "<td>%s</td>" % column_data
    return mark_safe(row_ele)

@register.simple_tag
def render_page_ele(loop_counter,query_sets,filter_condtions):
    filters = ''
    for k,v in filter_condtions.items():
        filters += '&%s=%s'%(k,v)

    # query_sets.number  当前页
    if abs(query_sets.number - loop_counter) <= 2:
        ele_class = ''
        if query_sets.number == loop_counter:
            ele_class = 'active'
        ele = '''<li class="%s"><a href="?page=%s%s">%s</a></li>'''%(ele_class,loop_counter,filters,loop_counter)

        return  mark_safe(ele)
    return ''

@register.simple_tag
def render_pages(query_sets,filter_condtions,previous_order_key,search_text):
    page_btns = ''

    filters = ''
    for k,v in filter_condtions.items():
        filters += '&%s=%s'%(k,v)

    added_dot_ele = False
    for page_num in query_sets.paginator.page_range:

        # query_sets.number  当前页
        if abs(query_sets.number - page_num) <= 1 or page_num < 3 or page_num > query_sets.paginator.num_pages - 2:
            ele_class = ''
            if query_sets.number == page_num:
                ele_class = 'active'
            page_btns += '''<li class="%s"><a href="?page=%s%s&o=%s&_q=%s">%s</a></li>'''%(ele_class,page_num,filters,previous_order_key,search_text,page_num)
            added_dot_ele = False
        else:
            if added_dot_ele is False:
                page_btns += '<li><a>...</a></li>'
                added_dot_ele = True

    return mark_safe(page_btns)

@register.simple_tag
def render_req_filter(filter_conditions):
    filter_str = ''
    for k,v in filter_conditions.items():
        filter_str += '&%s=%s'%(k,v)

    return filter_str


@register.simple_tag
def render_filter_ele(condtion,admin_class,filter_condtions):
    print('filter-->',filter_condtions)
    #这里增加一个默认不选的option
    select_ele = '''<select class="form-control" name='{filter_field}'><option value=''>----</option>'''
    #这里涉及select下拉框选项常见的两类：choices类和外键类，所以需要区分
    field_obj = admin_class.model._meta.get_field(condtion)
    if type(field_obj).__name__ not in ['DateTimeField','DateField']:
        if field_obj.choices:
            choice_data = field_obj.choices
        if type(field_obj).__name__ == 'ForeignKey':
            # 这里的1主要过滤掉  其前面不需要的横线
            choice_data = field_obj.get_choices()[1:]
        for choice_item in choice_data:
            selected = ''
            #这里需要注意的是  前端提交过来的筛选条件是字符串  对比注意数据类型
            if filter_condtions.get(condtion) == str(choice_item[0]):  #filter_condtions获取值最好用get，因为前端提交过来的空值是会过滤掉的，而condtion则是你在admin中定义的，字典没有的值，用get不会报错
                selected = 'selected'
            select_ele += '''<option value='%s' %s>%s</option>'''%(choice_item[0],selected,choice_item[1])

        filter_field_name = condtion
    #日期字段
    else:
        date_els = []
        today_ele = datetime.now().date()
        date_els.append(('今天',datetime.now().date()))
        date_els.append(('昨天',today_ele - timedelta(days=1)))
        date_els.append(('近7天',today_ele - timedelta(days=7)))
        date_els.append(('本月',today_ele.replace(day=1)))
        date_els.append(('近30天',today_ele - timedelta(days=30)))
        date_els.append(('近90天',today_ele - timedelta(days=90)))
        date_els.append(('近180天',today_ele - timedelta(days=180)))
        date_els.append(('本年',today_ele.replace(month=1,day=1)))
        date_els.append(('近一年',today_ele - timedelta(days=180)))
        for item in date_els:
            selected = ''
            filter_key = '%s__gte'%condtion
            if item[1].strftime('%Y-%m-%d') == str(filter_condtions.get(filter_key)):
                selected = 'selected'
            select_ele += '''<option value='%s' %s>%s</option>'''%(item[1],selected,item[0])

        filter_field_name = '%s__gte'%condtion

    select_ele += '</select>'
    select_ele = select_ele.format(filter_field=filter_field_name)
    return mark_safe(select_ele)

@register.simple_tag
def build_table_header_column(column,order_key,filter_condtions,search_text,admin_class):
    filter_str = ''
    for k,v in filter_condtions.items():
        filter_str += '&%s=%s'%(k,v)

    ele = '''<th>
    <a href="?o={order_key}{filter_str}&_q={search_text}">{column}</a>
    {sort_icon}
    </th>'''
    if order_key:

        if column == order_key.strip('-'):  #排序当前字段
            # 正序
            if '-' in order_key:
                sort_icon = '''<span class="glyphicon glyphicon-triangle-bottom" aria-hidden="true"></span>'''

            else:
                sort_icon = '''<span class="glyphicon glyphicon-triangle-top" aria-hidden="true"></span>'''
        else:
            order_key = column
            sort_icon = ''
    else:  #没有排序
        order_key = column
        sort_icon = ''

    try:
        column_verbose_name = admin_class.model._meta.get_field(column).verbose_name
    except FieldDoesNotExist as e:
        column_verbose_name = getattr(admin_class,column).display_name
        ele = '''<th><a href="javascript:void(0);">{column}</a></th>'''.format(column=column_verbose_name)
        return mark_safe(ele)
    ele = ele.format(order_key=order_key, column=column_verbose_name,sort_icon=sort_icon,filter_str=filter_str,search_text=search_text)
    return mark_safe(ele)


@register.simple_tag
def get_model_name(admin_class):
    return admin_class.model._meta.verbose_name_plural

@register.simple_tag
def get_m2m_obj_list(admin_class,field,form_obj):
    '''返回m2m所有待选数据'''

    #表结构对象的某个字段
    field_obj = getattr(admin_class.model,field.name)

    all_obj_list = field_obj.rel.to.objects.all()
    #单条数据的对象中的某个字段
    try:
        obj_instance_field = getattr(form_obj.instance,field.name)
        print(obj_instance_field)
        selected_obj_list = obj_instance_field.all()

        standby_obj_list = []
        for obj in all_obj_list:
            if obj not in selected_obj_list:
                standby_obj_list.append(obj)
    except:
        standby_obj_list = all_obj_list
    return standby_obj_list



@register.simple_tag
def get_m2m_selected_obj_list(form_obj,field):
    '''返回已选择的m2m数据'''
    try:
        field_obj = getattr(form_obj.instance,field.name)
        return field_obj.all()
    except:
        #当form_obj中没有数据时
        return []



def recursive_related_objs_lookup(objs):
    ul_ele = "<ul>"

    for obj in objs:
        li_ele = '''<li>%s : %s</li>'''%(obj._meta.verbose_name,obj.__unicode__().strip('<>'))
        ul_ele += li_ele

        #for local many to many
        #把所有跟这个对象直接关系的m2m字段取出来
        for m2m_field in obj._meta.local_many_to_many:
            sub_ul_ele = "<ul>"
            #getattr(customer,'tags')
            m2m_field_obj = getattr(obj,m2m_field.name)
            for o in m2m_field_obj.select_related():  #customer.tags.select_related()
                li_ele = '''<li>%s : %s</li>'''%(m2m_field.verbose_name,o.__unicode__())
                sub_ul_ele += li_ele

            sub_ul_ele += "</ul>"
            ul_ele += sub_ul_ele

        for related_obj in obj._meta.related_objects:
            if 'ManyToOneRel' not in related_obj.__repr__():
                continue

            #hasattr(customer,'enrollment_set')
            if hasattr(obj,related_obj.get_accessor_name()):
                accessor_obj = getattr(obj,related_obj.get_accessor_name())
                #上面accessor_obj  相当于   customer.enrollment_set

                #select_related()   ==  all()
                if hasattr(accessor_obj,'select_related'):
                    target_objs = accessor_obj.select_related()
                    # target_objs  相当于   customer.enrollment_set.all()
                else:
                    print("one to one i guess",accessor_obj)
                    target_objs = accessor_obj

                if len(target_objs) > 0:
                    nodes = recursive_related_objs_lookup(target_objs)
                    ul_ele += nodes

    ul_ele += "</ul>"
    return ul_ele


@register.simple_tag
def display_all_related_objs(objs):
    try:
        objs[0]
    except Exception as e:
        print('error info ',e)
        objs = [objs,]
    if objs:
        model_class = objs[0]._meta.model
        mode_name = objs[0]._meta.model_name
        #开始递归查找
        return mark_safe(recursive_related_objs_lookup(objs))

@register.simple_tag
def print_obj_methods(obj):
    print('-------------debug %s----------'%obj)
    return dir(obj)

@register.simple_tag
def get_action_verbose_name(admin_class,action):
    action_func = getattr(admin_class,action)
    return action_func.display_name if hasattr(action_func,'display_name') else action