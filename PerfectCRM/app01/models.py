# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib.auth.models import User,AbstractBaseUser,BaseUserManager,PermissionsMixin

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe
# Create your models here.


class Customer(models.Model):
    '''客户信息表'''
    name = models.CharField(max_length=32, blank=True, null=True,help_text='报名后请写上真实姓名')  # blank对admin起作用，而null对数据库起作用，一般两个成对写上
    qq = models.CharField(max_length=64, unique=True)
    qq_name = models.CharField(max_length=64, blank=True, null=True)
    phone = models.CharField(max_length=64, blank=True, null=True)
    id_num = models.CharField(max_length=64, blank=True, null=True)
    email = models.EmailField(verbose_name='常用邮箱',blank=True, null=True)
    source_choices = ((0, '转介绍'),
                      (1, 'QQ群'),
                      (2, '官网'),
                      (3, '百度推广'),
                      (4, '51CTO'),
                      (5, '知乎'),
                      (6, '市场推广')
                      )
    source = models.SmallIntegerField(choices=source_choices)  # 小数字字段省空间
    referral_from = models.CharField(verbose_name='转介绍人qq', max_length=64, blank=True, null=True)

    consult_course = models.ForeignKey("Course", verbose_name='咨询课程')
    content = models.TextField(verbose_name='咨询详情')
    tags = models.ManyToManyField('Tag', blank=True, null=True)
    consultant = models.ForeignKey('UserProfile', verbose_name='销售顾问')
    memo = models.TextField(blank=True, null=True, verbose_name='备注')
    status_choices = (
        (0,'未报名'),
        (1,'已报名'),
    )
    status = models.SmallIntegerField(default=0,choices=status_choices)
    date = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.qq

    class Meta:
        verbose_name = "客户信息表"  #设置了这个，在admin中就可以显示中文，不过这个还会加上一个1个s
        verbose_name_plural = "客户信息表"  #这个就不会加s


class Tag(models.Model):
    '''标签表，给客户打标签'''
    name = models.CharField(unique=True, max_length=32)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name_plural = "标签表"


class CustomerFollowUp(models.Model):
    '''客户跟踪记录表'''
    customer = models.ForeignKey('Customer')
    content = models.TextField(verbose_name='跟进内容')
    consultant = models.ForeignKey('UserProfile', verbose_name='跟进人')
    intention_choices = ((0, '2周内报名'),
                         (1, '1个月内报名'),
                         (2, '近期无报名计划'),
                         (3, '已在其他机构报名'),
                         (4, '已报名'),
                         (5, '已拉黑')
                         )

    intention = models.SmallIntegerField(choices=intention_choices)
    date = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return "<%s : %s>" % (self.customer.qq, self.intention)

    class Meta:
        verbose_name_plural = "客户跟踪记录表"


class Course(models.Model):
    '''课程表，在这里与班级一对多，一个课程可以多个班，创建班级时，选择课程'''
    name = models.CharField(max_length=64, unique=True)
    price = models.PositiveSmallIntegerField(verbose_name='课程价格')
    period = models.PositiveSmallIntegerField(verbose_name='周期（月）')
    outline = models.TextField(verbose_name='课程大纲')

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name_plural = "课程表"


class Branch(models.Model):
    '''校区'''
    name = models.CharField(max_length=128, unique=True)
    addr = models.CharField(max_length=128)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name_plural = "校区"


class ClassList(models.Model):
    '''班级表'''
    brance = models.ForeignKey('Branch', verbose_name='校区')
    course = models.ForeignKey('Course')
    class_type_choices = ((0, '面授（脱产）'),
                          (1, '面授（周末）'),
                          (2, '网络班'),
                          )
    class_type = models.SmallIntegerField(choices=class_type_choices, verbose_name='班级类型')
    contract = models.ForeignKey('ContractTemplate',blank=True,null=True)


    semester = models.PositiveSmallIntegerField(verbose_name='学期')
    teachers = models.ManyToManyField('UserProfile')
    start_date = models.DateTimeField(verbose_name='开班日期')
    end_date = models.DateTimeField(verbose_name='结业日期', blank=True, null=True)

    def __unicode__(self):
        return "%s %s %s" % (self.brance, self.course, self.semester)

    class Meta:
        unique_together = ('brance', 'course', 'semester')
        verbose_name_plural = '班级表'



class CourseRecord(models.Model):
    '''上课记录（课时） 一个班级有多节课，一个课时会有多个学生记录，主要记录哪个老师上，上课时间...'''
    from_class = models.ForeignKey("ClassList", verbose_name='班级')
    day_num = models.PositiveSmallIntegerField(verbose_name='第几节')
    teacher = models.ForeignKey('UserProfile')
    has_homework = models.BooleanField(default=True)
    homework_title = models.CharField(max_length=128, blank=True, null=True)
    homework_content = models.TextField(blank=True, null=True)
    outline = models.TextField(verbose_name='本节课程大纲')

    date = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return "%s %s" % (self.from_class, self.day_num)

    class Meta:
        unique_together = ('from_class', 'day_num')
        verbose_name_plural = '上课记录表'


class StudyRecord(models.Model):
    '''学习记录表'''
    student = models.ForeignKey('Enrollment')
    course_record = models.ForeignKey('CourseRecord')
    attendance_choices = ((0, '已签到'),
                          (1, '迟到'),
                          (2, '缺勤'),
                          (3, '早退'),
                          )
    attendance = models.SmallIntegerField(choices=attendance_choices, default=0)
    score_choices = ((100,'A+'),
                     (90, 'A'),
                     (85, 'B+'),
                     (80, 'B'),
                     (75, 'B-'),
                     (70, 'C+'),
                     (60, 'C'),
                     (40, 'C-'),
                     (-50, 'D'),
                     (-100, 'COPY'),
                     (0, 'N/A'),
                     )
    score = models.SmallIntegerField(choices=score_choices, default=0)
    memo = models.TextField(blank=True, null=True, verbose_name='备注(评语)')
    date = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return "%s %s %s" % (self.student, self.course_record, self.score)

    class Meta:
        unique_together = ('student','course_record')
        verbose_name_plural = "学习记录"


class Enrollment(models.Model):
    '''报名表，主要考虑一个客户可能报多个班'''
    customer = models.ForeignKey('Customer')
    enrolled_class = models.ForeignKey('ClassList', verbose_name='所报班级')

    consultant = models.ForeignKey('UserProfile', verbose_name='课程顾问')

    contract_agreed = models.BooleanField(default=False, verbose_name='学员已同意合同')
    contract_approved = models.BooleanField(default=False, verbose_name='合同已审核')
    date = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return "%s %s" % (self.customer, self.enrolled_class)

    class Meta:
        unique_together = ('customer', 'enrolled_class')
        verbose_name_plural = '报名表'


class Payment(models.Model):
    '''缴费记录'''
    customer = models.ForeignKey('Customer')
    course = models.ForeignKey("Course")
    amount = models.PositiveIntegerField(verbose_name='数额', default=500)
    consultant = models.ForeignKey('UserProfile')
    date = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return '%s %s' % (self.customer, self.amount)

    class Meta:
        verbose_name_plural = "缴费记录表"


class ContractTemplate(models.Model):
    '''合同模板'''
    name = models.CharField("合同名称",max_length=64,unique=True)
    template = models.TextField()

    def __unicode__(self):
        return self.name


class UserProfileManager(BaseUserManager):
    def create_user(self, email, name, password=None):
        """
        Creates and saves a User with the given email, date of
        birth and password.
        """
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email),  #对email格式验证
            name=name,
        )

        #设置密码  密文
        user.set_password(password)
        user.is_active = True  #可以登录
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, password):
        """
        Creates and saves a superuser with the given email, date of
        birth and password.
        """
        user = self.create_user(
            email,
            password=password,
            name=name,
        )
        user.is_active = True  # 可以登录
        user.is_admin = True  #是不是管理员（超级权限）
        user.save(using=self._db)
        return user



class UserProfile(AbstractBaseUser,PermissionsMixin):
    '''账号表'''
    email = models.EmailField(
        verbose_name='email address',
        max_length=255,
        unique=True,
        null=True
    )
    roles = models.ManyToManyField("Role",blank=True)
    password = models.CharField(_('password'), max_length=128,help_text=mark_safe(
        '''<a href='password/'>修改密码</a>'''
    ))
    # date_of_birth = models.DateField()
    name = models.CharField(max_length=32)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    objects = UserProfileManager()  #用于添加用户，修改密码啥的 objects  字段名固定死

    stu_account = models.ForeignKey("Customer",verbose_name='关联学员账号',blank=True,null=True,help_text='只有学员报名后方可为其创建账号')
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']  #额外添加的字段，需要在这里添加

    def get_full_name(self):
        # The user is identified by their email address
        return self.email

    def get_short_name(self):
        # The user is identified by their email address
        return self.email

    def __str__(self):  # __unicode__ on Python 2
        return self.email

    # def has_perm(self, perm, obj=None):
    #     "Does the user have a specific permission?"
    #     # Simplest possible answer: Yes, always
    #     return True
    #
    # def has_module_perms(self, app_label):
    #     "Does the user have permissions to view the app `app_label`?"
    #     # Simplest possible answer: Yes, always
    #     return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        # return self.is_admin
        return self.is_active

    #添加  权限选择项
    class Meta:
        permissions = (
            ('can_fuck_him_to_death','弄死你'),
            ('can_access_my_course','可以查看我的课程'),
            ('can_access_customer_list','可以查看客户列表'),
            ('can_access_customer_detail','可以查看客户详细信息'),
            ('can_upload_homework','可以交作业'),
        )


# class UserProfile(models.Model):
#     '''账号表'''
#     user = models.OneToOneField(User)
#     name = models.CharField(max_length=32)
#     roles = models.ManyToManyField('Role', blank=True, null=True)
#
#     def __unicode__(self):
#         return self.name
#
#     class Meta:
#         verbose_name_plural = "账号表"


class Role(models.Model):
    '''角色表'''
    name = models.CharField(max_length=32, unique=True)
    menus = models.ManyToManyField('Menu',blank=True)
    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name_plural = "角色表"


class Menu(models.Model):
    '''菜单'''
    name = models.CharField(max_length=32)
    url_type_choices = ((0,'alias'),(1,'absolute_url'))
    url_type = models.SmallIntegerField(choices=url_type_choices,default=0)
    url_name = models.CharField(max_length=64)  #request url 有别名存别名  没有就存url

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name_plural = '菜单表'