from django.shortcuts import HttpResponse, render, redirect
from django.http import JsonResponse
from apps.web.forms import wiki
from django.urls import reverse
from apps.web import models
from django.views.decorators.csrf import csrf_exempt
from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client
import sys
import os
import logging
from tracer import loacl_settings
import random
from django.views.decorators.clickjacking import xframe_options_sameorigin


def wiki_add(request, project_id):
    """添加wiki文档"""
    if request.method == 'GET':
        form = wiki.wikimodelform(request)
        return render(request, 'web/wiki_add.html', {'form': form})
    form = wiki.wikimodelform(request, data=request.POST)
    if form.is_valid():
        """表单并未填写项目信息， 手动输入中间件的"""
        # 判断用户是否选择夫文章
        if form.instance.father_id:
            form.instance.depth = form.instance.depth + 1
        else:
            form.instance.depth = 1
        form.instance.project_id = request.tracer.project
        form.save()
        url = reverse('web:wiki', kwargs={'project_id': project_id})
        return redirect(url)
    return render(request, 'web/wiki_add.html', {'form': form})


def wiki_catalog(request, project_id):
    """获取wiki目录"""
    # data = models.wiki.objects.filter(project_id=request.tracer.project).values_list('id', 'title', 'father_id')元组 下面是字典
    data = models.wiki.objects.filter(project_id=request.tracer.project).values('id', 'title', 'father_id').order_by('depth', 'id')
    return JsonResponse({'status': True, 'data': list(data)})
# def wiki_look(request, project_id):
#     """查看文章"""
#     return HttpResponse("ok")


def wiki_delete(request, project_id, wiki_id):
    """删除wiki"""
    models.wiki.objects.filter(project_id=project_id, id=wiki_id).delete()
    url = reverse('web:wiki', kwargs={'project_id': project_id})
    return redirect(url)

def wiki_edit(request, project_id, wiki_id):
    """编辑wiki"""
    if request.method == 'GET':
        wiki_object = models.wiki.objects.filter(project_id=project_id, id=wiki_id).first()
        form = wiki.wikimodelform(request, instance=wiki_object)
        return render(request, 'web/wiki_add.html', {'form': form})

    wiki_object = models.wiki.objects.filter(project_id=project_id, id=wiki_id).first()
    form = wiki.wikimodelform(request, data=request.POST, instance=wiki_object)
    if form.is_valid():
        """表单并未填写项目信息， 手动输入中间件的"""
        # 判断用户是否选择夫文章
        if form.instance.father_id:
            form.instance.depth = form.instance.depth + 1
        else:
            form.instance.depth = 1
        form.instance.project_id = request.tracer.project
        form.save()
        url = reverse('web:wiki', kwargs={'project_id': project_id})
        return redirect(url)
    return render(request, 'web/wiki_add.html', {'form': form})


@csrf_exempt
@xframe_options_sameorigin
def wiki_upload(request, project_id):
    """上传图片"""
    image_object = request.FILES.get('editormd-image-file')
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    ext = image_object.name.rsplit('.')[-1]
    randoms = '{}.{}'.format(random.randrange(1000000000, 9999999999), ext)
    # 1. 设置用户属性, 包括 secret_id, secret_key, region等。Appid 已在 CosConfig 中移除，请在参数 Bucket 中带上 Appid。Bucket 由 BucketName-Appid 组成
    secret_id = 'AKIDmcaTCviP1WzMYbS8d2Shmne4HG4lIgBV'  # 用户的 SecretId，建议使用子账号密钥，授权遵循最小权限指引，降低使用风险。子账号密钥获取可参见 https://cloud.tencent.com/document/product/598/37140
    secret_key = loacl_settings.secret_key  # 用户的 SecretKey，建议使用子账号密钥，授权遵循最小权限指引，降低使用风险。子账号密钥获取可参见 https://cloud.tencent.com/document/product/598/37140
    region = 'ap-chengdu'  # 替换为用户的 region，已创建桶归属的 region 可以在控制台查看，https://console.cloud.tencent.com/cos5/bucket
    # COS 支持的所有 region 列表参见 https://cloud.tencent.com/document/product/436/6224
    config = CosConfig(Region=region, SecretId=secret_id, SecretKey=secret_key)
    client = CosS3Client(config)

    #### 高级上传接口（推荐）
    # 根据文件大小自动选择简单上传或分块上传，分块上传具备断点续传功能。
    response = client.upload_file_from_buffer(
        Bucket=request.tracer.project.bucket,
        Body=image_object,
        Key=randoms,
    )
    print(response['ETag'])
    image_url = "https://{}.cos.{}.myqcloud.com/{}".format(request.tracer.project.bucket, request.tracer.project.region, randoms)
    print("image", image_url)
    result = {
        'success': 1,
        'message': None,
        'url': image_url
    }
    print(result)
    return JsonResponse(result)


