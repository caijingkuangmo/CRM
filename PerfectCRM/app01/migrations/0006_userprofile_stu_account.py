# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2018-02-23 03:11
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app01', '0005_auto_20180214_2131'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='stu_account',
            field=models.ForeignKey(blank=True, help_text='\u53ea\u6709\u5b66\u5458\u62a5\u540d\u540e\u65b9\u53ef\u4e3a\u5176\u521b\u5efa\u8d26\u53f7', null=True, on_delete=django.db.models.deletion.CASCADE, to='app01.Customer', verbose_name='\u5173\u8054\u5b66\u5458\u8d26\u53f7'),
        ),
    ]