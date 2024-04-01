from django.shortcuts import render, HttpResponse, redirect
from apps.web.forms.account import RegisterModelForm, login_sms, login_username
from django.http import JsonResponse
from apps.web import models
from django.db.models import Q
from django.core.exceptions import ValidationError
from django.conf import settings
def index(request):
    return render(request, 'web/index.html')

def login_out(request):
    """退出登录"""
    request.session.flush()
    return redirect('web:index')