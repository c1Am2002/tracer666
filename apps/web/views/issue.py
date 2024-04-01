from django.shortcuts import render
from django.shortcuts import HttpResponse
from django.http import JsonResponse
from django.utils import timezone
from apps.web import models
import json
from apps.web.views.account import uid
import datetime
from django.utils.safestring import mark_safe
from apps.web.forms.file import FileCreateForm
from django.shortcuts import render
from django.urls import reverse
from utlis.pagination import Pagination
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.clickjacking import xframe_options_sameorigin
from apps.web.forms.issues import IssuesModelForm, IssuesReplyModelForm, InviteModelForm
from django.core.exceptions import FieldDoesNotExist


def issue_detail(request, project_id, issue_id):
    """编辑问题"""
    issues_object = models.Issues.objects.filter(id=issue_id, project_id=project_id).first()
    form = IssuesModelForm(request, instance=issues_object)
    return render(request, 'web/issue_detail.html', {'form': form, "issue_object": issues_object})


class SelectFilter(object):
    def __init__(self, name, data_list, request):
        self.name = name
        self.data_list = data_list
        self.request = request

    def __iter__(self):
        yield mark_safe("<select class='select2' multiple='multiple' style='width:100%;' >")
        for item in self.data_list:
            key = str(item[0])
            text = item[1]

            selected = ""
            value_list = self.request.GET.getlist(self.name)
            if key in value_list:
                selected = 'selected'
                value_list.remove(key)
            else:
                value_list.append(key)

            query_dict = self.request.GET.copy()
            query_dict._mutable = True
            query_dict.setlist(self.name, value_list)
            if 'page' in query_dict:
                query_dict.pop('page')

            param_url = query_dict.urlencode()
            if param_url:
                url = "{}?{}".format(self.request.path_info, param_url)  # status=1&status=2&status=3&xx=1
            else:
                url = self.request.path_info

            html = "<option value='{url}' {selected} >{text}</option>".format(url=url, selected=selected, text=text)
            yield mark_safe(html)
        yield mark_safe("</select>")


class CheckFilter(object):
    def __init__(self, name, data_list, request):
        """name是不同的字段， data_list是字段所能选择的选择， request用于获取url"""
        self.name = name
        self.data_list = data_list
        self.request = request

    def __iter__(self):
        for item in self.data_list:
            """key是每个选择前面的id ，value是每个选项id对应的文本"""
            key = str(item[0])
            text = item[1]
            ck = ""
            # 如果当前用户请求的URL中status和当前循环key相等
            value_list = self.request.GET.getlist(self.name)
            """checken能实现✔ 如果原本就是勾， 那么这次点击就是取消打勾"""
            if key in value_list:
                ck = 'checked'
                value_list.remove(key)
            else:
                value_list.append(key)

            # 为自己生成URL
            # 在当前URL的基础上去增加一项
            # status=1&age=19
            from django.http import QueryDict
            """复制当前url"""
            query_dict = self.request.GET.copy()
            query_dict._mutable = True
            query_dict.setlist(self.name, value_list)
            if 'page' in query_dict:
                query_dict.pop('page')

            param_url = query_dict.urlencode()
            if param_url:
                """拼接url"""
                url = "{}?{}".format(self.request.path_info, param_url)  # status=1&status=2&status=3&xx=1
            else:
                url = self.request.path_info

            tpl = '<a class="cell" href="{url}"><input type="checkbox" {ck} /><label>{text}</label></a>'
            """生成筛选界面"""
            html = tpl.format(url=url, ck=ck, text=text)
            yield mark_safe(html)


@csrf_exempt
@xframe_options_sameorigin
def issue_replay(request, project_id, issue_id):
    """评论展示"""
    if request.method == "GET":
        reply_list = models.IssuesReply.objects.filter(issues_id=issue_id, issues__project=request.tracer.project)
        # 将queryset转换为json格式
        data_list = []
        for row in reply_list:
            data = {
                'id': row.id,
                'reply_type_text': row.get_reply_type_display(),
                'content': row.content,
                'creator': row.creator.name,
                'datetime': row.create_datetime.strftime("%Y-%m-%d %H:%M"),
                'parent_id': row.reply_id
            }
            data_list.append(data)

        return JsonResponse({'status': True, 'data': data_list})

    form = IssuesReplyModelForm(data=request.POST)
    if form.is_valid():
        form.instance.issues_id = issue_id
        form.instance.reply_type = 2
        form.instance.creator = request.tracer.user
        instance = form.save()
        info = {
            'id': instance.id,
            'reply_type_text': instance.get_reply_type_display(),
            'content': instance.content,
            'creator': instance.creator.name,
            'datetime': instance.create_datetime.strftime("%Y-%m-%d %H:%M"),
            'parent_id': instance.reply_id
        }

        return JsonResponse({'status': True, 'data': info})
    return JsonResponse({'status': False, 'error': form.errors})

@csrf_exempt
@xframe_options_sameorigin
def issue_change(request, project_id, issue_id):
    """
        {'name': 'subject', 'value': '好饿呀sdfasdf'}
        {'name': 'subject', 'value': ''}

        {'name': 'desc', 'value': '好饿呀sdfasdf'}
        {'name': 'desc', 'value': ''}

        {'name': 'start_date', 'value': '好饿呀sdfasdf'}
        {'name': 'end_date', 'value': '好饿呀sdfasdf'}

        {'name': 'issues_type', 'value': '2'}
        {'name': 'assign', 'value': '4'}
        """
    issues_object = models.Issues.objects.filter(id=issue_id, project_id=project_id).first()
    post_dict = json.loads(request.body.decode('utf-8'))
    print(post_dict)
    name = post_dict.get('name')
    value = post_dict.get('value')
    field_object = models.Issues._meta.get_field(name)

    def create_reply_record(content):
        """添加数据到问题回复表"""
        new_object = models.IssuesReply.objects.create(
            reply_type=1,
            issues=issues_object,
            content=content,
            creator=request.tracer.user,
        )
        """给前端返回值用于展示操作记录"""
        new_reply_dict = {
            'id': new_object.id,
            'reply_type_text': new_object.get_reply_type_display(),
            'content': new_object.content,
            'creator': new_object.creator.name,
            'datetime': new_object.create_datetime.strftime("%Y-%m-%d %H:%M"),
            'parent_id': new_object.reply_id
        }
        return new_reply_dict
    if name in ["subject", 'desc', 'start_date', 'end_date']:
        if not value:
            """判断数据是否为空 和数据库的字段是否允许为空"""
            if not field_object.null:
                return JsonResponse({'status': False, 'error': "该字段不能为空"})
            setattr(issues_object, name, None)
            issues_object.save()
            change_record = "{}将{}更新为空".format(request.tracer.user.name, field_object.verbose_name)
        else:
            setattr(issues_object, post_dict['name'], post_dict['value'])
            issues_object.save()
            # 记录：xx更为了value
            change_record = "{}将{}更新为{}".format(request.tracer.user.name, field_object.verbose_name, post_dict['value'])

        return JsonResponse({'status': True, 'data': create_reply_record(change_record)})

# 1.2 FK字段（指派的话要判断是否创建者或参与者）
    if name in ['issues_type', 'module', 'parent', 'assign']:
        # 用户选择为空
        if not value:
            # 不允许为空
            if not field_object.null:
                return JsonResponse({'status': False, 'error': "该字段不能为空"})
            # 允许为空
            setattr(issues_object,  name, None)
            issues_object.save()
            change_record = "{}更新为空".format(field_object.verbose_name)
        else:  # 用户输入不为空
            if name == 'assign':
                # 是否是项目创建者
                if value == str(request.tracer.project.create_name_id):
                    instance = request.tracer.project.create_name
                else:
                    project_user_object = models.project_people.objects.filter(project_id_id=project_id, user_id=value).first()
                    if project_user_object:
                        instance = project_user_object.user
                    else:
                        instance = None
                if not instance:
                    return JsonResponse({'status': False, 'error': "选择的值不存在"})

                setattr(issues_object, name, instance)
                issues_object.save()
                change_record = "{}更新为{}".format(field_object.verbose_name, str(instance))  # value根据文本获取到内容
            else:
                # 条件判断：用户输入的值，是自己的值。remote_field.model会将前面的每个外键跳转到它所依赖的表， 相当于跨表查询
                instance = field_object.remote_field.model.objects.filter(id=value, project_id=project_id).first()
                if not instance:
                    return JsonResponse({'status': False, 'error': "选择的值不存在"})

                setattr(issues_object, name, instance)
                issues_object.save()
                """下面的str， instance是跨到各个表查询到的值， 用str会返回model所定义的str的值"""
                change_record = "{}将{}更新为{}".format(request.tracer.user.name, field_object.verbose_name, str(instance))  # value根据文本获取到内容

        return JsonResponse({'status': True, 'data': create_reply_record(change_record)})

# 1.3 choices字段
    if name in ['priority', 'status', 'mode']:
        texts = None
        for key, text in field_object.choices:
            if str(key) == value:
                texts = text
        if not texts:
            return JsonResponse({'status': False, 'error': "选择的值不存在"})
        setattr(issues_object, name, value)
        issues_object.save()
        change_record = "{}将{}更新为{}".format(request.tracer.user.name, field_object.verbose_name, texts)
        return JsonResponse({'status': True, 'data': create_reply_record(change_record)})

# M2M字段
    if name == "attention":
        # {"name":"attention","value":[1,2,3]}
        # 判断格式是否整正确
        if not isinstance(value, list):
            return JsonResponse({'status': False, 'error': "数据格式错误"})
        # 判断是否将值改为空
        if not value:
            issues_object.attention.set(value)
            issues_object.save()
            change_record = "{}将{}更新为空".format(request.tracer.user.name, field_object.verbose_name)
        else:
            # values=["1","2,3,4]  ->   id是否是项目成员（参与者、创建者）
            # 获取当前项目的所有成员
            # 添加创建者
            user_dict = {str(request.tracer.project.create_name_id): request.tracer.project.create_name.name}
            project_user_list = models.project_people.objects.filter(project_id_id=project_id)
            for item in project_user_list:
                user_dict[str(item.user_id)] = item.user.name
            username_list = []
            # 添加创建者和参与者用于输出
            for user_id in value:
                username = user_dict.get(str(user_id))
                if not username:
                    return JsonResponse({'status': False, 'error': "用户不存在请重新设置"})
                username_list.append(username)

            issues_object.attention.set(value)
            issues_object.save()
            change_record = "{}将{}更新为{}".format(request.tracer.user.name, field_object.verbose_name, ",".join(username_list))

        return JsonResponse({'status': True, 'data': create_reply_record(change_record)})


def invite_url(request, project_id):
    """ 生成邀请码 """

    form = InviteModelForm(data=request.POST)
    if form.is_valid():
        """
        1. 创建随机的邀请码
        2. 验证码保存到数据库
        3. 限制：只有创建者才能邀请
        """
        if request.tracer.user != request.tracer.project.create_name:
            form.add_error('period', "只有项目创建者能生成邀请码")
            return JsonResponse({'status': False, 'error': form.errors})
        random_invite_code = uid(request.tracer.user.MobelPhone)
        form.instance.project = request.tracer.project
        form.instance.code = random_invite_code
        form.instance.creator = request.tracer.user
        form.save()

        # 将验邀请码返回给前端，前端页面上展示出来。
        url = "{scheme}://{host}{path}".format(
            scheme=request.scheme,
            host=request.get_host(),
            path=reverse('web:invite_join', kwargs={'code': random_invite_code})
        )

        return JsonResponse({'status': True, 'data': url})

    return JsonResponse({'status': False, 'error': form.errors})


def invite_join(request, code):
    """ 访问邀请码 """

    invite_object = models.ProjectInvite.objects.filter(code=code).first()
    if not invite_object:
        return render(request, 'web/invite_join.html', {'error': '邀请码不存在'})

    if invite_object.project.create_name == request.tracer.user:
        return render(request, 'web/invite_join.html', {'error': '创建者无需再加入项目'})

    exists = models.project_people.objects.filter(project_id=invite_object.project, user=request.tracer.user).exists()
    if exists:
        return render(request, 'web/invite_join.html', {'error': '已加入项目无需再加入'})

    # 最多允许的成员
    # max_member = request.tracer.trade.prices.project_member_num
    max_member = 0
    amx_trade = models.trade.objects.filter(user_id=invite_object.creator).order_by('-id').first()
    if amx_trade.prices.cate == 1:
        max_member = 2
    else:
        """判断会员是否过期"""
        if amx_trade.end_time < datetime.datetime.now():
            max_member = 2
        else:
            max_member = amx_trade.prices.project_member_num
    # 目前所有成员(创建者&参与者）
    current_member = models.project_people.objects.filter(project_id=invite_object.project).count()
    current_member = current_member + 1
    if current_member >= max_member:
        return render(request, 'web/invite_join.html', {'error': '项目成员超限已超出最大限制'})

    # 邀请码是否过期？, 第一种用于默认时间 ，第二种用于将时区改为东八区， 并且设置USE_TZ = False
    # current_datetime = timezone.now()
    current_datetime = datetime.datetime.now()
    limit_datetime = invite_object.create_datetime + datetime.timedelta(minutes=invite_object.period)
    if current_datetime > limit_datetime:
        return render(request, 'web/invite_join.html', {'error': '邀请码已过期'})

    # # 数量限制？, 存在并超出限制
    # if invite_object.count:
    #     if invite_object.use_count >= invite_object.count:
    #         return render(request, 'web/invite_join.html', {'error': '邀请码数据已使用完'})
    #     invite_object.use_count += 1
    #     invite_object.save()
    invite_object.use_count += 1
    invite_object.save()
    models.project_people.objects.create(user=request.tracer.user, project_id=invite_object.project)
    invite_object.project.participants_num += 1
    invite_object.project.save()
    return render(request, 'web/invite_join.html', {'project': invite_object.project})



