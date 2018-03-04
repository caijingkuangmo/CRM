#! /usr/bin/env python
# -*- coding:utf-8 -*-
__author__ = "laoliu"

from app01 import models
from django.shortcuts import render,redirect,HttpResponse

enabled_admins = {}

class BaseAdmin(object):
    '''防止子类继承如果没写，执行过程依然能找到，只不过为空'''
    list_display = []  #显示的列
    list_filters = []  #筛选条件
    search_fields = []  #对哪些字段进行搜索
    list_per_page = 20  #每页显示多少条
    ordering = None  #默认排序的列
    filter_horizontal = []  #哪些多对多字段的复选框显示两框
    readonly_fields = []  #哪些字段只读
    readonly_table = False  #整张表是否只读
    actions = ['delete_selected_objs', ]  #订制操作
    modelform_exclude_fields = []  #在被form渲染前端时，排除这些字段  不显示

    def delete_selected_objs(self,request,querysets):
        print('--->',self,request,querysets)
        app_name = self.model._meta.app_label
        table_name = self.model._meta.model_name
        errors = {}
        # 表只读 不能删除  直接报错
        if self.readonly_table:
            errors = {'readonly_table': "This table is readonly,cannot be deleted"}
        if "yes" == request.POST.get('delete_confirm'):
            #做第二件事
            if not self.readonly_table:
                querysets.delete()
                return redirect("/king_admin/%s/%s/"%(app_name,table_name))
        selected_ids = ','.join([str(i.id) for i in querysets])
        #做第一件事
        return render(request,"king_admin/table_obj_delete.html",{"objs":querysets,
                                                                  'admin_class':self,
                                                                  'app_name':app_name,
                                                                  'table_name':table_name,
                                                                  'selected_ids':selected_ids,
                                                                  'action':request._admin_action,
                                                                  'errors':errors})

    @staticmethod
    def default_form_validation(self):  #对所有字段验证的方法
        '''用户可以在此进行自定义的表单验证 相当于django form的clean方法'''
        pass



class CustomerAdmin(BaseAdmin):
    list_display = ('id','qq','name','source','consultant','consult_course','date','enroll')
    list_filters = ['source','consultant','consult_course','date']
    search_fields = ['qq','name','consultant__name']
    list_per_page = 5
    ordering = 'id'
    filter_horizontal = ('tags',)
    readonly_fields = ['qq','consultant','tags',]
    # readonly_table = True
    actions = ['delete_selected_objs','test',]

###############################################################
    #form  字段验证
    @staticmethod
    def default_form_validation(self):
        print('------customer validation',self)
        print('----instance',self.instance)

        consult_content = self.cleaned_data.get('content','')
        if len(consult_content) < 15:
            return self.ValidationError(
                    ('Field %(field)s 咨询内容不能少于15个字符'),
                    code='invalid',
                    params={'field':'content'},
                )

    @staticmethod
    def clean_name(self):  #对name字段验证
        print("name clean validation:",self.cleaned_data["name"])
        if not self.cleaned_data["name"]:
            self.add_error("name","cannot be null")


#####################################################
    #action操作
    def test(self,request,querysets):
        print('test')

    test.display_name = '测试动作'

######################################################
    #表外字段扩展
    def enroll(self):
        print("enroll",self.instance)
        if self.instance.status == 1:  #如果是已经报名的用户  还是可以报名其他课程的
            link_name = '报名新课程'
        else:
            link_name = '报名'

        #然后在跳转的url对应的页面  想干啥就干啥
        return '''<a href="/crm/customer/%s/enrollment/">%s</a>'''%(self.instance.id,link_name)

    enroll.display_name = '报名链接'


class CustomerFollowUpAdmin(BaseAdmin):
    list_display = ('customer','consultant','date')

class UserProfileAdmin(BaseAdmin):
    list_display = ('email','name')
    readonly_fields = ('password',)
    filter_horizontal = ('user_permissions','groups',)
    modelform_exclude_fields = ['last_login']


class CourseRecordAdmin(BaseAdmin):
    list_display = ['from_class','day_num','teacher','has_homework','homework_title','date']

    def initialize_studyrecords(self,request,queryset):
        print('--->initialize_studyrecords',self,request,queryset)
        if len(queryset) > 1:
            return HttpResponse("只能选择一个班级")

        #queryset[0]  为上课记录  也就是课时

        # 一次正向操作，课时表取班级   一次反向操作  班级表取报名对象  最终取到所有的报名学员
        print(queryset[0].from_class.enrollment_set.all())

        #get_or_create  有就不进行创建，没有才创建  create在有的情况下，是会唯一性 错误的
        # for enroll_obj in queryset[0].from_class.enrollment_set.all():
        #     models.StudyRecord.objects.get_or_create(
        #         student = enroll_obj,
        #         course_record = queryset[0],
        #         attendance = 0,
        #         score = 0,
        #     )
        #不过上面方式存在问题，也就是get_or_create执行过程包括了commit，即是每次循环都操作了一次数据库，一旦数据量大了，就影响速度

        new_obj_list = []
        for enroll_obj in queryset[0].from_class.enrollment_set.all():
            new_obj_list.append(models.StudyRecord(
                student = enroll_obj,
                course_record = queryset[0],
                attendance = 0,
                score = 0,
            ))

        try:
            models.StudyRecord.objects.bulk_create(new_obj_list)  #批量创建，事物操作（原子性）
        except Exception as e:
            return HttpResponse('批量初始化学习记录失败，请检查该节课是否已经有对应的学习记录')



        return redirect('/king_admin/app01/studyrecord/?course_record=%s'%queryset[0].id)
    initialize_studyrecords.display_name = "初始化本节所有学员的上课记录"
    actions = ['initialize_studyrecords',]


class StudyRecordAdmin(BaseAdmin):
    list_display = ['student','course_record','attendance','score','date']
    list_filters = ['course_record','score','attendance']
    list_editable = ['score','attendance']





#注册函数
def register(model_class,admin_class=None):
    '''
    把  表类   和   自定义admin类   对应关系写入到enabled_admins字典中
    :param model_class: 表类  比如UserProfile
    :param admin_class: 自定义admin类
    :return: 
    '''
    app_name = model_class._meta.app_label
    table_name = model_class._meta.model_name
    if app_name not in enabled_admins:
        enabled_admins[app_name] = {}
    #我们会发现字典中存储 也只是 app名 和  表名 和  admin类对应关系，其实在这存储结构里 models类和admin类没有直接的关系
    #而表名是表类名的小写字符串，如果你觉得可以通过APP名和表名  反射 去操作 表类的一些属性，还是挺麻烦的
    #既然在这个函数里 传入了表类，何不在admin类上绑定一个属性 就是  表类，以便后面方面操作了？
    admin_class.model = model_class
    enabled_admins[app_name][table_name] = admin_class

register(models.Customer,CustomerAdmin)
register(models.UserProfile,UserProfileAdmin)
register(models.CustomerFollowUp,CustomerFollowUpAdmin)
register(models.CourseRecord,CourseRecordAdmin)
register(models.StudyRecord,StudyRecordAdmin)