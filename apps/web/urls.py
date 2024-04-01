from django.contrib import admin
from django.urls import path, include
from apps.app01 import views
from apps.web.views import account, home, project, managee,wiki, file, seeting, issue, overview, statistics
from django.urls import re_path
app_name = 'web'
urlpatterns = [
    # path(r'^register/$', account.register)
    path('reg/', account.register, name='register'),
    # path('sms/', account.send_sms, name = 'send_sms'),
    path('login_sms/', account.login, name='login'),
    path("login_username/", account.login_name, name='login_username'),
    path("img_code/", account.img_code, name='img_code'),
    path("index/", home.index, name='index'),
    path('login_out/', home.login_out, name='login_out'),
    path('project_list', project.project_list, name='project_list'),
    path('moneny', account.moneny, name='moneny'),
    #星标
    re_path(r'^project_start/(?P<project_type>\w+)/(?P<project_id>\d+)/$', project.project_start, name='project_start'),
    # path('project_start/<str:project_type>/<int:project_id>/', project.project_start, name='project_start')
    re_path(r'^project_unstart/(?P<project_type>\w+)/(?P<project_id>\d+)/$', project.project_unstart, name= 'project_unstart'),
    #项目管理
    re_path(r'^manage/(?P<project_id>\d+)/', include([
        re_path(r'^issue/$', managee.issue, name='issue'),
        re_path(r'^issue_replay/(?P<issue_id>\d+)$', issue.issue_replay, name='issue_replay'),
        re_path(r'^issue_change/(?P<issue_id>\d+)$', issue.issue_change, name='issue_change'),
        re_path(r'^issue_detail/(?P<issue_id>\d+)$', issue.issue_detail, name='issue_detail'),
        re_path(r'^issues_invite_url/$', issue.invite_url, name='invite_url'),
        re_path(r'^statistics/$', managee.statistics, name='statistics'),
        re_path(r'^statistics_priority/$', statistics.statistics_priority, name='statistics_priority'),
        re_path(r'^statistics_project_user/$', statistics.statistics_project_user, name='statistics_project_user'),
        re_path(r'^file/$', managee.file,  name='file'),
        re_path(r'^file_delete/$', file.file_delete,  name='file_delete'),
        re_path(r'^file_post/$', file.file_post,  name='file_post'),
        re_path(r'^file_download/(?P<file_id>\d+)/$', file.file_download, name='file_download'),
        re_path(r'^cos_credential/$', file.cos_credential, name='cos_credential'),
        re_path(r'^wiki/$', managee.wiki, name='wiki'),
        re_path(r'^wiki_add/$', wiki.wiki_add, name='wiki_add'),
        re_path(r'^wiki_catalog/$', wiki.wiki_catalog, name='wiki_catalog'),
        # re_path(r'^wiki_look/$', wiki.wiki_look, name='wiki_look'),
        re_path(r'^wiki_delete/(?P<wiki_id>\d+)/$', wiki.wiki_delete, name='wiki_delete'),
        re_path(r'^wiki_eidt/(?P<wiki_id>\d+)/$', wiki.wiki_edit, name='wiki_edit'),
        re_path(r'^wiki_upload/$', wiki.wiki_upload, name='wiki_upload'),
        re_path(r'^seeting/$', managee.seeting, name='seeting'),
        re_path(r'^seeting_delete$', seeting.seeting_delete, name='seeting_delete'),
        re_path(r'^overview/$', overview.overview, name='overview'),
        re_path(r'^overview_issues_chart/$', overview.issues_chart, name='issues_chart'),
    ], None)),
    re_path(r'^invite_join/(?P<code>\w+)/$', issue.invite_join, name='invite_join'),
    # re_path(r'^manage/(?P<project_id>\d+)/overview/$', project.project_start, name='project_start'),
    # re_path(r'^manage/(?P<project_id>\d+)/issue/$', project.project_start, name='project_start'),
    # re_path(r'^manage/(?P<project_id>\d+)/statistics/$', project.project_start, name='project_start'),
    # re_path(r'^manage/(?P<project_id>\d+)/file/$', project.project_start, name='project_start'),
    # re_path(r'^manage/(?P<project_id>\d+)/wiki/$', project.project_start, name='project_start'),
    # re_path(r'^manage/(?P<project_id>\d+)/seeting/$', project.project_start, name='project_start'),
]
