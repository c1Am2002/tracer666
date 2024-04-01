from django.shortcuts import HttpResponse, render, redirect
from django.http import JsonResponse
from django.urls import reverse
from utlis.tencent.cos_qqq import delete_file, delete_manyfile, credential, delete_bucket
from apps.web.forms.file import FileModelForm
from apps.web import models
import json
import requests
from django.views.decorators.csrf import csrf_exempt
from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client
import sys
import os
import logging
from tracer import loacl_settings
import random
from django.views.decorators.clickjacking import xframe_options_sameorigin


def seeting_delete(request, project_id):
    """删除桶中文件和碎片文件并删除桶"""
    if request.method == 'GET':
        return render(request, 'web/seeting_delete.html')

    project_name = request.POST.get('project_name')
    live_project = models.project.objects.filter(create_name=request.tracer.user)
    project_names = None
    for live in live_project:
        if project_name == live.project_name:
            project_names = project_name
    if not project_name:
        return render(request, 'web/seeting_delete.html', {'error': "项目名错误"})
    if not project_names:
        return render(request, 'web/seeting_delete.html', {'error': "你没有创建该项目"})
    # 项目名写对了则删除（只有创建者可以删除）
    if request.tracer.user != request.tracer.project.create_name:
        return render(request, 'web/seeting_delete.html', {'error': "只有项目创建者可删除项目"})

    # 1. 删除桶
    #       - 删除桶中的所有文件（找到桶中的所有文件 + 删除文件 )
    #       - 删除桶中的所有碎片（找到桶中的所有碎片 + 删除碎片 )
    #       - 删除桶
    # 2. 删除项目
    #       - 项目删除
    delete_bucket(bucket=request.tracer.project.bucket, region='ap-chengdu')
    models.project.objects.filter(project_name=project_names).delete()
    return redirect('web:project_list')
