import collections
from django.shortcuts import render
from apps.web import models
from django.http import JsonResponse
from django.db.models import Count
import time
import datetime


def overview(request, project_id):
    """ 概览 """

    # 问题数据处理
    # status_dict = collections.OrderedDict()
    status_dict = {}
    for key, text in models.Issues.status_choices:
        status_dict[key] = {'text': text, 'count': 0}

    issues_data = models.Issues.objects.filter(project_id=project_id).values('status').annotate(ct=Count('id'))
    for item in issues_data:
        status_dict[item['status']]['count'] = item['ct']

    # 项目成员
    user_list = models.project_people.objects.filter(project_id_id=project_id).values('user_id', 'user__name')

    # 最近的10个问题
    top_ten = models.Issues.objects.filter(project_id=project_id, assign__isnull=False).order_by('-id')[0:10]

    context = {
        'status_dict': status_dict,
        'user_list': user_list,
        'top_ten_object': top_ten
    }
    return render(request, 'web/overview.html', context)

def issues_chart(request, project_id):
    """ 在概览页面生成highcharts所需的数据 """
    """首先生成当前时间的前30天， 
    然后将他们的参数设置每一天的时间：对应的时间戳，0， 然后遍历查询到的数据， 将相应的时间的0改为创建的问题数"""
    today = datetime.datetime.now().date()
    date_dict = collections.OrderedDict()
    for i in range(0, 30):
        date = today - datetime.timedelta(days=i)
        date_dict[date.strftime("%Y-%m-%d")] = [time.mktime(date.timetuple()) * 1000, 0]

    # select xxxx,1 as ctime from xxxx
    # select id,name,email from table;
    # select id,name, strftime("%Y-%m-%d",create_datetime) as ctime from table;
    # "DATE_FORMAT(web_transaction.create_datetime,'%%Y-%%m-%%d')"
    result = models.Issues.objects.filter(project_id=project_id,
                                          create_datetime__gte=today - datetime.timedelta(days=30)).extra(
        select={'ctime': "DATE_FORMAT(web_issues.create_datetime,'%%Y-%%m-%%d')"}).values('ctime').annotate(ct=Count('id'))

    for item in result:
        date_dict[item['ctime']][1] = item['ct']

    return JsonResponse({'status': True, 'data': list(date_dict.values())})