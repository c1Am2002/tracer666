from django.shortcuts import HttpResponse, render, redirect
from django.http import JsonResponse
from django.urls import reverse
from utlis.tencent.cos_qqq import delete_file, delete_manyfile, credential
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


def file_delete(request, project_id):
    """删除文件"""
    f_id = request.GET.get('fid')
    delete_object = models.FileRepository.objects.filter(id=f_id, project=request.tracer.project).first()
    if delete_object.file_type == 1:
        """删除文件"""
        """从数据库中删除项目所占空间（字节）"""
        request.tracer.project.use_space = request.tracer.project.use_space - delete_object.file_size
        request.tracer.project.save()
        """从cos中删除"""
        delete_file(Bucket=request.tracer.project.bucket, region='ap-chengdu', key=delete_object.key)
        """数据库中删除"""
        delete_object.delete()
        return JsonResponse({'status': True})

    else:
        """删除文件夹"""
        total_size = 0
        key_list = []
        delete_list = [delete_object, ]
        for file in delete_list:
            child_list = models.FileRepository.objects.filter(project=request.tracer.project, parent=file).order_by('-file_type')
            for child in child_list:
                if child.file_type == 2:
                    """将所要删除的文件夹下的文件夹收集"""
                    delete_list.append(child)
                else:
                    total_size += child.file_size
                    key_list.append({'Key': child.key})
        if key_list:
            """批量删除文件"""
            delete_manyfile(Bucket=request.tracer.project.bucket, region='ap-chengdu', key_lsit=key_list)

        request.tracer.project.use_space = request.tracer.project.use_space - total_size
        request.tracer.project.save()
        delete_object.delete()
        return JsonResponse({'status':True})


@xframe_options_sameorigin
@csrf_exempt
def cos_credential(request, project_id):
    file_list = json.loads(request.body.decode('utf-8'))
    total_size = 0
    """做容量限制"""
    """单文件限制"""
    for item in file_list:
        """item['size']获取文件字节大小"""
        size = request.tracer.trade.prices.file_size
        """将m转换为字节"""
        if item['size'] > size * 1024 * 1024:
            print(item['size'])
            return JsonResponse({'status':False,
                                 'error': "{}文件过大, 请传入小于{}M的文件".format(item['name'], request.tracer.trade.prices.file_size)
                                 })
        total_size += item['size']
    """获取项目总空间和已经使用的空间"""
    sum_size = request.tracer.trade.prices.space_size * 1024 * 1024
    sized = request.tracer.project.use_space
    print(sized)
    print(sized + total_size)
    if sized + total_size > sum_size:
        return JsonResponse({'status': False, 'error': "添加文件， 已经超出了最大容量"})
    data_dict = credential(request.tracer.project.bucket, request.tracer.project.region)
    return JsonResponse({'status':True, 'data':data_dict})


@xframe_options_sameorigin
@csrf_exempt
def file_post(request, project_id):
    form = FileModelForm(request, data=request.POST)
    if form.is_valid():
        """将上传成功的文件写入数据库"""
        file_dict = form.cleaned_data
        file_dict.pop('etag')
        file_dict.update({'project': request.tracer.project, 'update_user': request.tracer.user, 'file_type': 1})
        instance = models.FileRepository.objects.create(**file_dict)
        request.tracer.project.use_space += file_dict['file_size']
        request.tracer.project.save()
        result = {
            'name': instance.name,
            'file_type': instance.get_file_type_display(),
        }
        return JsonResponse({'status': True, 'data': result})
    return JsonResponse({'status': False, 'data': "cuccccccc"})


def file_download(request, project_id, file_id):
    """下载文件, 获取文件内容并设置响应头"""
    file_obj = models.FileRepository.objects.filter(id=file_id, project=request.tracer.project).first()
    contention = requests.get(file_obj.file_path)
    data = contention.content
    respon = HttpResponse(data)
    """设置响应头"""
    respon['Content-Disposition'] = 'attachment; filename={}'.format(file_obj.name)
    return respon

