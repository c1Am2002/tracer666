from django.utils.deprecation import MiddlewareMixin
from apps.web import models
from django.shortcuts import redirect
from django.conf import settings
import datetime
class tracer(object):
    def __init__(self):
        self.user = None
        self.trade = None
        self.project = None
class middle_ware(MiddlewareMixin):
    def process_request(self, request):
        """如果用户登录 那么在request中赋值"""
        # tracer_object = tracer()
        request.tracer = tracer()
        user_id = request.session.get('user_id', 0)
        user_object = models.UserInfo.objects.filter(name=user_id).first()
        # tracer_object.user = user_object
        # request.tracer = tracer_object
        request.tracer.user = user_object
        """如果没有登录 无法访问个人页面"""
        if request.path_info in settings.WHITE_URL_LIST:
            return
        if not request.tracer:
            return redirect('web:login_username')
        """获取当前用户的id值最大（也就是最新的）交易记录"""
        now_time = datetime.datetime.now()
        user_trade = models.trade.objects.filter(user_id=user_object, state=1).order_by('-id').first()
        """判断收费版是否存在并且已过期"""
        if user_trade and user_trade.end_time and user_trade.end_time < now_time:
            """过期的话就当作免费版处理"""
            user_trade = models.trade.objects.filter(user_id=user_object, state=1, prices=1).first()
        # tracer_object.trade = user_trade
        # request.tracer = tracer_object
        request.tracer.trade = user_trade

    def process_view(self, request, view, args, kwargs):
        """如果url不是项目栏 或者url是项目栏，但是是我创建的或者我参与的项目都可以访问，
        否则返回个人主页 并通过将request中封装一个对象，从而在前端更好判断"""
        if not request.path_info.startswith('/web/manage/'):
            return
        project_id = kwargs.get('project_id')
        my_project = models.project.objects.filter(id=project_id, create_name= request.tracer.user).first()
        if my_project:
            request.tracer.project = my_project
            return
        join_project = models.project_people.objects.filter(id=project_id, user=request.tracer.user).first()
        if join_project:
            request.tracer.project = join_project.project_id
            return
        return redirect('web:project_list')
