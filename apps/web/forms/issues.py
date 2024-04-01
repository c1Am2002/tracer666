from apps.web.forms import boot_form
from django import forms
from apps.web import models


class IssuesModelForm(boot_form.boot_form, forms.ModelForm):
    class Meta:
        model = models.Issues
        exclude = ['project', 'creator', 'create_datetime', 'latest_update_datetime']
        widgets = {
            "assign": forms.Select(attrs={'class': "selectpicker", "data-live-search": "true"}),
            "attention": forms.SelectMultiple(
                attrs={'class': "selectpicker", "data-live-search": "true", "data-actions-box": "true"}),
            "parent": forms.Select(attrs={'class': "selectpicker", "data-live-search": "true"}),
        }

    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 给每一个问题的问题类型设置为当前项目所拥有的问题类型
        self.fields['issues_type'].choices = models.IssuesType.objects.filter(project=request.tracer.project).values_list('id', 'title')

        # 给每一个问题的模块类型设置为当前项目所拥有的模块类型， 并且模块类型可以为空
        total_list = [('', '-------'), ]
        mokuai_list = models.Module.objects.filter(project=request.tracer.project).values_list('id', 'title')
        total_list.extend(mokuai_list)
        self.fields['module'].choices = total_list

        # 对于指派和关注
        total_user_list = [(request.tracer.project.create_name.id, request.tracer.project.create_name.name), ]
        join_user_list = models.project_people.objects.filter(project_id=request.tracer.project).values_list('user_id', 'user__name')
        total_user_list.extend(join_user_list)

        self.fields['assign'].choices = total_user_list
        self.fields['attention'].choices = total_user_list

        # 父问题
        totals_list = [('', '-------'), ]
        mokuais_list = models.Issues.objects.filter(project=request.tracer.project).values_list('id', 'subject')
        totals_list.extend(mokuais_list)
        self.fields['parent'].choices = totals_list


class IssuesReplyModelForm(forms.ModelForm):
    class Meta:
        model = models.IssuesReply
        fields = ['content', 'reply']


class InviteModelForm(boot_form.boot_form, forms.ModelForm):
    class Meta:
        model = models.ProjectInvite
        fields = ['period',]