from django.shortcuts import render, HttpResponse, redirect
from apps.web.forms.account import RegisterModelForm, login_sms, login_username
from django.http import JsonResponse
from apps.web import models
from django.db.models import Q
from apps.web.forms.project import project_modelform
from utlis.tencent.cos_qqq import create_bucket
import random
import time


def project_list(request):
    if request.method == 'GET':
        form = project_modelform(request)
        project_list = {'start': [], 'my': [], 'join': []}
        my_project = models.project.objects.filter(create_name=request.tracer.user)
        join_project = models.project_people.objects.filter(user=request.tracer.user)
        for starts in my_project:
            if starts.start:
                project_list['start'].append({'value':starts, 'type':'my'})
            else:
                project_list['my'].append(starts)
        for startss in join_project:
            if startss.start:
                project_list['start'].append({'value':startss.project_id, 'type':'my'})
            else:
                project_list['join'].append(startss.project_id)

        return render(request, 'web/project_list.html', {'form': form, 'project_list': project_list})
    else:
        form = project_modelform(request, data=request.POST)
        if form.is_valid():
            """创建桶"""
            times = int(time.time() * 1000)
            # randoms = random.randrange(1000000000, 9999999999)
            bultkon = "{}-{}-{}".format(request.tracer.user.MobelPhone, times, 1323906324)
            rangon = 'ap-chengdu'
            create_bucket(bultkon, rangon)
            """将创建人的数据, 桶的信息一并添加"""
            form.instance.bucket = bultkon
            form.instance.region = rangon
            form.instance.create_name = request.tracer.user
            # 为每个项目初始化问题类型
            instance = form.save()
            type_lists = []
            for item in models.IssuesType.type_list:
                type_lists.append(models.IssuesType(project=instance, title=item))
            # 批量添加
            models.IssuesType.objects.bulk_create(type_lists)
            return JsonResponse({'status': True})
        return JsonResponse({'status': False, "error": form.errors})


def project_start(request, project_type: str, project_id: int):
    if project_type == 'my':
        models.project.objects.filter(id=project_id, create_name=request.tracer.user).update(start=True)
        return redirect('web:project_list')
    elif project_type == 'join':
        models.project_people.objects.filter(project_id_id=project_id, user=request.tracer.user).update(start=True)
        return redirect('web:project_list')
    return HttpResponse("请求错误")

def project_unstart(request, project_type:str, project_id: int):
    if project_type == 'my':
        models.project.objects.filter(id=project_id, create_name=request.tracer.user).update(start=False)
        return redirect('web:project_list')
    elif project_type == 'join':
        models.project_people.objects.filter(project_id_id=project_id, user=request.tracer.user).update(start=False)
        return redirect('web:project_list')
    return HttpResponse("请求错误")
