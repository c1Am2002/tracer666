from django import forms
from apps.web.forms import boot_form
from apps.web import models
from django.core.exceptions import ValidationError
from apps.web.forms import widgets
class project_modelform(boot_form.boot_form, forms.ModelForm):
    def __init__(self,  request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request
    description = forms.CharField(label="请描述该项目", widget=forms.Textarea(attrs={'xxx':123}), required=False)

    class Meta:
        model = models.project
        fields = ['project_name', 'description', 'color']
        widgets = {
            'color': widgets.colorRadioSelect(attrs={'class': 'color-radio'})
        }

    def clean_project_name(self):
        project_name = self.cleaned_data['project_name']
        """同一个用户不能创建同名项目"""
        exists = models.project.objects.filter(project_name=project_name, create_name=self.request.tracer.user).exists()
        if exists:
            raise ValidationError("你已经创建了一个同名的项目")
        """判断用户是否还能创建项目"""
        """用户最多能创建几个项目"""
        num = self.request.tracer.trade.prices.create_project_num
        """用户已经创建的项目"""
        count = models.project.objects.filter(create_name=self.request.tracer.user).count()
        if num <= count:
            raise ValidationError("你无法再创建更多的项目，请充值")

        return project_name
