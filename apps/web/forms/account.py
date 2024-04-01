from django.shortcuts import render, HttpResponse
from utlis.tencent.sms import send_sms_single
from django_redis import get_redis_connection
from utlis.encrypt import md5
from django import forms
from django.conf import settings
from apps.web import models
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.db.models import Q
# from tracer import loacl_settings
import random
from apps.web.forms import boot_form
from utlis.tencent.sms import send_sms_single
# Create your views here.
# class boot_form(object):
#     """保持样式工整"""
#     def __init__(self,  *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         for name ,field in self.fields.items():
#             field.widget.attrs['class'] = 'form-control'

"""生成注册界面"""
class RegisterModelForm(boot_form.boot_form , forms.ModelForm):
    # phone = forms.IntegerField(label="电话")#将电话字段的char改为int
    # emali = forms.EmailField(label="邮箱", validators=[])
    name = forms.CharField(label="账号", widget=forms.TextInput(
        attrs={'placeholder': "请输入账号"}))
    email = forms.EmailField(label="邮箱号码", widget=forms.EmailInput(
        attrs={'placeholder': "请输入邮箱号"}
    ))
    MobelPhone = forms.CharField(label="电话", validators=[RegexValidator(r'^(1[3|4|5|6|7|8|9]\d{9})$', "手机号不存在"), ],
                                  widget=forms.NumberInput(
                                      attrs={'placeholder': "请输入手机号"}
                                  ))
    pwd = forms.CharField(label="密码",min_length=8, max_length=20, error_messages={'min_length':'密码长度不能小于8位', 'max_length':'密码长度不能大于20位'}, widget=forms.PasswordInput(
        attrs={'placeholder': "请输入密码"}
    ))
    re_pwd = forms.CharField(label="再次输入密码",min_length=8, max_length=20, error_messages={'min_length':'密码长度不能小于8位', 'max_length':'密码长度不能大于20位'}, widget=forms.PasswordInput(
        attrs={'placeholder':"请再次输入密码"}
    ))
    # code = forms.CharField(label="验证码", widget=forms.TextInput(
    #     attrs={'placeholder': "请输入验证码"}
    # ))
    class Meta:
        model = models.UserInfo
        fields = ['email', 'name', 'pwd', 're_pwd', 'MobelPhone']
    # def __init__(self,  *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     # self.request = request
    #     for name ,field in self.fields.items():
    #         field.widget.attrs['class'] = 'form-control'
            # field.widget.attrs['placeholder'] = field.label
            # field.widget.attrs['placeholder'] = '请输入%s' %(field.label,)#快速生成提示语
    def clean_email(self):
        email = self.cleaned_data['email']
        exit = models.UserInfo.objects.filter(email = email).exists()
        if exit:
            raise ValidationError("该邮箱已注册")
        else:
            return email
    def clean_name(self):
        name = self.cleaned_data['name']
        return name
    def clean_pwd(self):
        pwd = self.cleaned_data['pwd']
        return pwd
    def clean_re_pwd(self):
        pwd = self.cleaned_data['pwd']
        re_pwd = self.cleaned_data['re_pwd']
        if(pwd != re_pwd):
            raise ValidationError("密码不一致")
        else:
            return pwd
    def clean_MobelPhone(self):
        MobelPhone = self.cleaned_data['MobelPhone']
        exit = models.UserInfo.objects.filter(MobelPhone=MobelPhone).exists()
        if exit:
            raise ValidationError("手机号已存在")
        else:
            return MobelPhone
    # def clean_code(self):
    #     code = self.cleaned_data['code']
    #     MobelPhone = self.cleaned_data['MobelPhone']
    #     # MobelPhone = self.cleaned_data.get('MobelPhone')
    #     if MobelPhone is None:
    #         return code
    #     conn = get_redis_connection()
    #     frist_code = conn.get(MobelPhone)
    #     """将redis中的数据转为字符串"""
    #     if frist_code is None:
    #         raise ValidationError("验证码未发送，请稍等")
    #     else:
    #         str_code = frist_code.decode('utf-8')
    #         """判断验证码是否正确，并且去除验证码中误输入的空格，防止错误"""
    #         if code.strip() != str_code.strip():
    #             raise ValidationError("验证码错误")




# class SmsForms(forms.Form):
#     MobelPhone = forms.CharField(label='手机号', required=True, validators=[RegexValidator(r'^(1[3|4|5|6|7|8|9])\d{9}$', '手机号格式错误'), ])
#     """获取request对象"""
#     def __init__(self, request, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.request = request
#
#     def clear_MobelPhone(self):
#         MobelPhone = self.cleaned_data['MobelPhone']
#         """判断tple格式是否正确"""
#         tpl = self.request.GET.get('tpl')
#         tpl_id = settings.TENCENT_SMS_TEMPLEATE.get(tpl)
#
#
#         if not tpl_id:
#             raise ValidationError("tpl格式错误")
#         """判断手机号是否已注册"""
#         exists = models.UserInfo.objects.filter(MobelPhone=MobelPhone).exists()
#         if tpl == 'login':
#             if not exists:
#                 raise ValidationError("手机号未注册")
#         elif tpl == 'register':
#             if exists:
#                 raise ValidationError("手机号已存在")
#         """发短信"""
#         code = random.randrange(100000, 999999)
#         sms = send_sms_single(MobelPhone, tpl_id, [code,])
#         """result为0表示发送成功"""
#         if sms['result'] != 0:
#             raise ValidationError("短信发送失败, {}".format(sms['errmsg']))
#         """写redis"""
#         conn = get_redis_connection()
#         """redis中存储60秒"""
#         conn.set(MobelPhone, code, ex = 60)
#         return MobelPhone
class login_sms(boot_form.boot_form, forms.Form):
    # MobelPhone = forms.CharField(label='手机号', required=True,
    #                              validators=[RegexValidator(r'^(1[3|4|5|6|7|8|9])\d{9}$', '手机号不存在'), ])
    name = forms.CharField(label="手机号或邮箱", widget=forms.TextInput(
        attrs={'placeholder': "请输入手机号或邮箱"}))

    pwd = forms.CharField(label="密码", min_length=8, max_length=20,
                          error_messages={'min_length': '密码长度不能小于8位', 'max_length': '密码长度不能大于20位'},
                          widget=forms.PasswordInput(
                              attrs={'placeholder': "请输入密码"}, render_value=True
                          ))

    code_img = forms.CharField(label="图片验证码", widget=forms.TextInput(
        attrs={'placeholder': "请输入图片验证码"}))

    def __init__(self,  request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request

    # def clean_name(self):
    #     name = self.cleaned_data['name']
    #     # exit = models.UserInfo.objects.filter(MobelPhone=MobelPhone).exists()
    #     user_name = models.UserInfo.objects.filter(name=name).first()
    #     if not user_name:
    #         raise ValidationError("手机号未注册")
    #     else:
    #         return user_name

    def clean_pwd(self):
        pwd = self.cleaned_data['pwd']
        return pwd

    def clean_code_img(self):
        """用户输入的验证码"""
        code = self.cleaned_data['code_img']
        """session中的验证码, 使用get防止因为验证码过去而出现的错误"""
        img_code = self.request.session.get('img_code')
        if img_code is None:
            raise ValidationError("验证码已过期，请重新获取")
        elif code.upper() != img_code:
            raise ValidationError("验证码错误")
        else:
            return code


    # def clean_code(self):
    #     code = self.cleaned_data['code']
    #     # MobelPhone = self.cleaned_data['MobelPhone']
    #     user_name = self.cleaned_data.get('MobelPhone')
    #     """手机号不存在，验证码没法校验，由于手机号与验证码绑定"""
    #     if user_name is None:
    #         return code
    #     conn = get_redis_connection()
    #     frist_code = conn.get(user_name.MobelPhone)
    #     """将redis中的数据转为字符串"""
    #     if frist_code is None:
    #         raise ValidationError("验证码未发送，请稍等")
    #     else:
    #         str_code = frist_code.decode('utf-8')
    #         """判断验证码是否正确，并且去除验证码中误输入的空格，防止错误"""
    #         if code.strip() != str_code.strip():
    #             raise ValidationError("验证码错误")

class login_username(boot_form.boot_form, forms.Form):
    name = forms.CharField(label="用户名", widget=forms.TextInput(
        attrs={'placeholder': "请输入用户名"}))
    pwd = forms.CharField(label="密码", min_length=8, max_length=20,
                          error_messages={'min_length': '密码长度不能小于8位', 'max_length': '密码长度不能大于20位'},
                          widget=forms.PasswordInput(
                              attrs={'placeholder': "请输入密码"}, render_value= True
                          ))
    code_img = forms.CharField(label="图片验证码", widget=forms.TextInput(
        attrs={'placeholder': "请输入图片验证码"}))

    def __init__(self,  request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request

    def clean_pwd(self):
        pwd = self.cleaned_data['pwd']
        return pwd

    def clean_code_img(self):
        """用户输入的验证码"""
        code = self.cleaned_data['code_img']
        """session中的验证码, 使用get防止因为验证码过去而出现的错误"""
        img_code = self.request.session.get('img_code')
        if img_code is None:
            raise ValidationError("验证码已过期，请重新获取")
        elif code.upper() != img_code:
            raise ValidationError("验证码错误")
        else:
            return code









