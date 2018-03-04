# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render,HttpResponse
from app01 import models
from PerfectCRM import settings
import os,json,time
from app01.permissions import permission
# Create your views here.

@permission.check_permission
def stu_my_classes(req):
    return render(req,'student/my_classes.html')

def studyrecords(req,enroll_obj_id):
    enroll_obj = models.Enrollment.objects.get(id=enroll_obj_id)
    return render(req,'student/studyrecords.html',{'enroll_obj':enroll_obj})

def homework_detail(req,studyrecord_id):
    studyrecord_obj = models.StudyRecord.objects.get(id=studyrecord_id)

    homework_path = "{base_dir}/{class_id}/{course_record_id}/{studyrecord_id}/".format(
        base_dir=settings.HOMEWORK_DATA,
        class_id=studyrecord_obj.course_record.from_class_id,
        course_record_id=studyrecord_obj.course_record_id,
        studyrecord_id=studyrecord_obj.id
    )

    if not os.path.isdir(homework_path):
        os.makedirs(homework_path)


    if req.method == "POST":
        print(req.FILES)

        for k,file_obj in req.FILES.items():
            with open("%s/%s"%(homework_path,file_obj.name),'wb') as f:
                for chunk in file_obj.chunks():
                    f.write(chunk)

        # return HttpResponse(json.dumps({"status":0,"msg":"file upload success"}))

    file_lists = []
    for file_name in os.listdir(homework_path):
        f_path = "%s/%s" % (homework_path, file_name)
        modify_time = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(os.stat(f_path).st_mtime))
        file_lists.append([file_name, os.stat(f_path).st_size, modify_time])
    print("file lists", file_lists)

    if req.method == 'POST':
        return HttpResponse(json.dumps({"status": 0,
                                        "msg": "file upload success",
                                        "file_lists":file_lists}))

    return render(req,'student/homework_detail.html',{'studyrecord_obj':studyrecord_obj,
                                                      'file_lists':file_lists})
