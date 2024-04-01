from django.template import Library
from apps.web import models
from django.urls import reverse

register = Library()


@register.inclusion_tag('inclusion/all_project_list.html')
def all_project(request):
    my_project = models.project.objects.filter(create_name=request.tracer.user)
    join_project = models.project_people.objects.filter(user=request.tracer.user)
    return {'my': my_project, 'join': join_project, 'request':request}


@register.inclusion_tag('inclusion/menu_list.html')
def menu_list(request):
    project_id = request.tracer.project.id
    menu_list = [
        {'title': "概览", 'url': reverse("web:overview", kwargs={'project_id': project_id})},
        {'title': "问题", 'url': reverse("web:issue", kwargs={'project_id': project_id})},
        {'title': "统计", 'url': reverse("web:statistics", kwargs={'project_id': project_id})},
        {'title': "wiki", 'url': reverse("web:wiki", kwargs={'project_id': project_id})},
        {'title': "文件", 'url': reverse("web:file", kwargs={'project_id': project_id})},
        {'title': "设置", 'url': reverse("web:seeting", kwargs={'project_id': project_id})},

    ]
    for item in menu_list:
        if request.path_info.startswith(item['url']):
            item['class'] = 'active'
    return {'menu_list': menu_list}
