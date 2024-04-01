from django.shortcuts import render, HttpResponse
from utlis.tencent.sms import send_sms_single
import random
from django import forms
from django.conf import settings
from apps.app01 import models
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
# Create your views here.
def sent_sms(request):
    """
    发送注册账号短信
    ?type = login ->2055161
    ?type = register ->2055160
    ?tupe = renew ->2055159
    """
    # tpl = request.GET.get('type')
    #     # template_id = settings.TENCENT_SMS_TEMPLEATE.get(tpl)
    #     # if not template_id:
    #     #     return HttpResponse("格式错误")
    sum = random.randrange(100000, 999999)
    res = send_sms_single('18283222951', 2055161, [sum, ])
    print(res)
    return HttpResponse("发送成功")
"""生成注册界面"""
class RegisterModelForm(forms.ModelForm):
    # phone = forms.IntegerField(label="电话")#将电话字段的char改为int
    # emali = forms.EmailField(label="邮箱", validators=[])
    name = forms.CharField(label="账号", widget=forms.TextInput(
        attrs={'placeholder': "请输入账号"}))
    email = forms.EmailField(label="邮箱号码", widget=forms.EmailInput(
        attrs={'placeholder': "请输入邮箱号"}
    ))
    phone = forms.EmailField(label="电话", validators=[RegexValidator(r'^(1[3|4|5|6|7|8|9]\d{9}$', "手机号不存在"),], widget=forms.NumberInput(
        attrs={'placeholder': "请输入手机号"}
    ))
    pwd = forms.CharField(label="密码", widget=forms.PasswordInput(
        attrs={'placeholder': "请输入密码"}
    ))
    re_pwd = forms.CharField(label="再次输入密码", widget=forms.PasswordInput(
        attrs={'placeholder':"请再次输入密码"}
    ))
    code = forms.CharField(label="验证码", widget=forms.TextInput(
        attrs={'placeholder': "请输入验证码"}
    ))
    class Meta:
        model = models.UserInfo
        fields = ['email', 'name', 'pwd', 're_pwd', 'phone', 'code']
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name ,field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            # field.widget.attrs['placeholder'] = field.label
            # field.widget.attrs['placeholder'] = '请输入%s' %(field.label,)#快速生成提示语


def register(request):
    form = RegisterModelForm()
    return render(request, 'app01/register.html', {'form':form})

