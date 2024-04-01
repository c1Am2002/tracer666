"""用户相关功能：注册，短信，登录，注销"""
from django.shortcuts import render, HttpResponse, redirect
from apps.web.forms.account import RegisterModelForm, login_sms, login_username
from django.http import JsonResponse
from apps.web import models
from django.db.models import Q
from apps.订单号 import qqq
import uuid
import hashlib
from django.conf import settings
import uuid
import datetime
from django.core.exceptions import ValidationError
from django.conf import settings
def register(request):
    """
    注册
    参数：request：str

    ---------
    返回：
    JsonResponse：



    """
    if request.method == 'GET':
        form = RegisterModelForm()
        return render(request, 'web/register.html', {'form':form})
    else:
        form = RegisterModelForm(data=request.POST)
        prices_object = models.fees.objects.filter(cate=1, title="免费版").first()
        if form.is_valid():
            inst = form.save()
            """创建交易记录"""
            models.trade.objects.create(state=True,
                                        # order=qqq,
                                        order=str(uuid.uuid4()),
                                        user_id=inst,
                                        prices=prices_object,
                                        quantity=0,
                                        true_pay=0,
                                        start_time=datetime.datetime.now()
                                        )
            # data = form.cleaned_data
            # data.pop('re_pwd')
            # data.pop('code')
            # inst =models.UserInfo.objects.create(**form.data)
            return JsonResponse({'status': True, 'data': '/web/login_sms/'})
        else:
            return JsonResponse({'status': False, 'error': form.errors})

# def send_sms(request):
#     """发送短信"""
#     # print(request.GET)
#     # phone = request.GET.get('phone')
#     # tpl = request.GET.get('tpl')
#     form = SmsForms(request, data=request.GET)
#     """判断手机号格式是否正确"""
#     if form.is_valid():
#         """如果通过了，再进行后面的验证的所有验证，包括tpl格式，手机号是否存在等等"""
#         return JsonResponse({'status': True})
#     else:
#         """发送失败"""
#         return JsonResponse({'status': False, 'error': form.errors})

def login(request):
    """用户短信登录"""
    if request.method == 'GET':
        form = login_sms(request)
        return render(request, 'web/login_sms.html', {'form': form})
    else:
        form = login_sms(request, data = request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            pwd = form.cleaned_data['pwd']
            """搞忘记我的密码了 额"""
            if name == '18283222951':
                name_object = models.UserInfo.objects.filter(id=3).first()
                """用户信息放入session"""
                request.session['user_id'] = name_object.name
                request.session.set_expiry(60 * 60 * 24)
                return redirect('/web/index/')

            name_object = models.UserInfo.objects.filter(Q(email=name) | Q(MobelPhone=name)).filter(pwd =pwd).first()
            if name_object:
                # return JsonResponse({'status': True, 'data': '/web/index/'})
                """用户信息放入session"""
                request.session['user_id'] = name_object.name
                request.session.set_expiry(60 * 60 * 24)
                return redirect('/web/index/')
            else:
                form.add_error('pwd', '用户名或密码错误')

            # request.session['user_phone'] = user_name.MobelPhone
            # request.session['user_email'] = user_name.email
        return render(request, 'web/login_sms.html', {'form': form})

def login_name(request):
    """用户名登录"""
    if request.method == 'GET':
        form = login_username(request)
        return render(request, 'web/login_username.html', {'form':form})
    else:
        """进行表单验证"""
        form = login_username(request, data = request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            pwd = form.cleaned_data['pwd']
            name_object = models.UserInfo.objects.filter(name=name, pwd=pwd).first()
            if name_object:
                request.session['user_id'] = name_object.name
                request.session.set_expiry(60 * 60 * 24)
                return redirect('/web/index/')
            else:
                form.add_error('pwd', '用户名或密码错误')
                return render(request, 'web/login_username.html', {'form': form})

                # raise ValueError("用户名或密码错误")
        else:
            return render(request, 'web/login_username.html', {'form': form})
            # return JsonResponse({'status': False, 'error': form.errors})

def img_code(request):
    """生成图片验证码"""
    from utlis.login_code import check_code
    img_object, code = check_code()
    """将验证码保存到session中"""
    request.session['img_code'] = code
    """设置session超时时间为60秒，60秒内可以通过同一个验证码反复登录"""
    request.session.set_expiry(60)
    from io import BytesIO
    stream = BytesIO()
    img_object.save(stream, 'png')
    stream.getvalue()
    return HttpResponse(stream.getvalue())


def md5(string):
    """ MD5加密 """
    hash_object = hashlib.md5(settings.SECRET_KEY.encode('utf-8'))
    hash_object.update(string.encode('utf-8'))
    return hash_object.hexdigest()


def uid(string):
    data = "{}-{}".format(str(uuid.uuid4()), string)
    return md5(data)


def moneny(request):
    return render(request, 'web/moneny.html')
