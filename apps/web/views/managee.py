from django.shortcuts import render
from django.shortcuts import HttpResponse
from django.http import JsonResponse
from apps.web import models
from apps.web.forms.file import FileCreateForm
from django.shortcuts import render
from utlis.pagination import Pagination
from apps.web.views.issue import CheckFilter, SelectFilter
from apps.web.forms.issues import IssuesModelForm, InviteModelForm



def issue(request, project_id):
    if request.method == 'GET':
        # 分页获取数据
        # 根据URL做筛选，筛选条件（根据用户通过GET传过来的参数实现）
        # ?status=1&status=2&issues_type=1
        allow_filter_name = ['issues_type', 'status', 'priority', 'assign', 'attention']
        condition = {}
        for name in allow_filter_name:
            value_list = request.GET.getlist(name)  # [1,2]
            if not value_list:
                continue
            condition["{}__in".format(name)] = value_list
        quesrset = models.Issues.objects.filter(project_id=project_id).filter(**condition)
        page_obj = Pagination(
            current_page=request.GET.get('page'),
            all_count=quesrset.count(),
            base_url=request.path_info,
            query_params=request.GET,
            per_page=2
        )
        form = IssuesModelForm(request)
        # 分页展示数据
        issue_list = quesrset[page_obj.start:page_obj.end]
        # 将外键类型通过特定的数据获取格式 装化成类似的选择类型
        project_issues_type = models.IssuesType.objects.filter(project_id=project_id).values_list('id', 'title')
        # 获取当前项目的所有人 包括参与人和创建人
        project_total_user = [(request.tracer.project.create_name.id, request.tracer.project.create_name.name,)]
        join_user = models.project_people.objects.filter(project_id_id=project_id).values_list('user_id', 'user__name')
        project_total_user.extend(join_user)
        invite_form = InviteModelForm()
        content = {
            'form': form,
            'issue_list': issue_list,
            'invite_form': invite_form,
            'page_html': page_obj.page_html,
            'lists' : [
            {'title': "状态", 'filter': CheckFilter('status', models.Issues.status_choices, request)},
            {'title': "优先级", 'filter': CheckFilter('priority', models.Issues.priority_choices, request)},
            {'title': "问题类型", 'filter': CheckFilter('issues_type', project_issues_type, request)},
            {'title': "指派者", 'filter': SelectFilter('assign', project_total_user, request)},
            {'title': "关注者", 'filter': SelectFilter('attention', project_total_user, request)},
            ]
        }
        return render(request, 'web/issue.html', content)

    form = IssuesModelForm(request, data=request.POST)
    if form.is_valid():
        form.instance.project = request.tracer.project
        form.instance.creator = request.tracer.user
        form.save()
        return JsonResponse({'status':True})
    return JsonResponse({'status':False, "error":form.errors})


def statistics(request, project_id):
    return render(request, 'web/statistics.html')


def file(request, project_id):
    """添加文件夹和访问文件"""
    parent_object = None
    folder_id = request.GET.get('folder', '')
    if folder_id and folder_id.isdecimal():
        parent_object = models.FileRepository.objects.filter(id=folder_id, project_id=request.tracer.project, file_type=2).first()
    if request.method == 'GET':
        """导航条"""
        bread_list = []
        parent_obj = parent_object
        while parent_obj:
            """由于是父id 所以是一直往前面插， 如果是子id 直接append就行了"""
            bread_list.insert(0, {'id': parent_obj.id, 'name': parent_obj.name})
            parent_obj = parent_obj.parent
        queryser = models.FileRepository.objects.filter(project=request.tracer.project)
        if parent_object:
            """展示该文件夹下的文件或文件夹"""
            file_list = queryser.filter(parent=parent_object).order_by('-file_type')
        else:
            file_list = queryser.filter(parent__isnull=True).order_by('-file_type')
        form = FileCreateForm()
        return render(request, 'web/file.html', {'form': form, 'file_list': file_list, 'bread_list': bread_list, 'folder_object': parent_object})
    """获取文件id 并判断文件是否存在"""
    """添加文件和修改文件"""
    fid = request.POST.get('fid', '')
    f_obj = None
    if fid and fid.isdecimal():
        f_obj = models.FileRepository.objects.filter(project=request.tracer.project, id=fid, file_type=2).first()
    if f_obj:
        form = FileCreateForm(request.POST, instance=f_obj)
    else:
        form = FileCreateForm(request.POST)
    if form.is_valid():
        form.instance.project = request.tracer.project
        form.instance.file_type = 2
        form.instance.parent = parent_object
        form.instance.update_user = request.tracer.user
        form.save()
        data = '/web/manage/{}/file/'.format(project_id)
        return JsonResponse({'status': True})
    return JsonResponse({'status': False, 'error': form.errors})



def wiki(request, project_id):
    """获取当前的wiki， 用于预览"""
    wiki_id = request.GET.get('wiki_id')
    if not wiki_id or not wiki_id.isdecimal():
        return render(request, 'web/wiki.html')
    else:
        data_object = models.wiki.objects.filter(id=wiki_id, project_id=request.tracer.project).first()
        return render(request, 'web/wiki.html', {'data_object':data_object})


def seeting(request, project_id):
    return render(request, 'web/seeting.html')
