from django.db import models

# Create your models here.
class UserInfo(models.Model):
    name = models.CharField(verbose_name="用户名", max_length=16)
    email = models.EmailField(verbose_name="邮箱", max_length=32)
    MobelPhone = models.CharField(verbose_name="手机号", max_length=12, blank=False, null=False)
    pwd = models.CharField(verbose_name="密码", max_length=32)

    def __str__(self):
        return self.name

    # class Meta:
    #     app_label = 'apps.web_label'

class fees(models.Model):
    cate_choices = (
        (1, '免费版'),
        (2, '收费版'),
        (3, '尊享版'),
    )
    cate = models.SmallIntegerField(verbose_name="收费类型", default=1, choices=cate_choices)
    title = models.CharField(verbose_name="类型", max_length=16)
    """正整数类型"""
    prices = models.PositiveIntegerField(verbose_name="价格/年")
    create_project_num = models.PositiveIntegerField(verbose_name="创建项目个数")
    project_member_num = models.PositiveIntegerField(verbose_name="每个项目最大成员数")
    space_size = models.PositiveIntegerField(verbose_name="每个项目空间大小/m")
    file_size = models.PositiveIntegerField(verbose_name="单文件大小/m")
    create_time = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)

class project(models.Model):
    color_choices = (
        (1, '#56b8eb'),
        (2, '#f28033'),
        (3, '#ebc656'),
        (4, '#a2d148'),
        (5, '#20BFA4'),
        (6, '#7461c2'),
        (7, '#20bfa3'),
    )
    project_name = models.CharField(verbose_name="项目名", max_length=16)
    description = models.CharField(verbose_name="项目描述", max_length=256, null=True, blank=True)
    color = models.SmallIntegerField(verbose_name="颜色", choices=color_choices, default=1)
    start = models.BooleanField(verbose_name="星标", default=False)
    use_space = models.BigIntegerField(verbose_name="项目使用空间", default=0, help_text="字节")
    participants_num = models.IntegerField(verbose_name="参与人数", default=1)
    create_name = models.ForeignKey(verbose_name="创建人", to="UserInfo", on_delete=models.CASCADE)
    create_time = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)
    bucket = models.CharField(verbose_name="桶名", max_length=128)
    region = models.CharField(verbose_name="cos区域", max_length=32)

class wiki(models.Model):
    title = models.CharField(verbose_name="标题", max_length=32)
    text = models.TextField(verbose_name="正文")
    depth = models.IntegerField(verbose_name="深度", default=1)
    project_id = models.ForeignKey(verbose_name="项目名", to="project", on_delete=models.CASCADE)
    """自关联并且生成反向关联"""
    father_id = models.ForeignKey(verbose_name="父文章", to="wiki", blank=True, null=True, on_delete=models.CASCADE, related_name="children")
    def __str__(self):
        return self.title


class FileRepository(models.Model):
    """ 文件库 """
    project = models.ForeignKey(verbose_name='项目', to='project', on_delete=models.CASCADE)
    file_type_choices = (
        (1, '文件'),
        (2, '文件夹')
    )
    file_type = models.SmallIntegerField(verbose_name='类型', choices=file_type_choices)
    name = models.CharField(verbose_name='文件夹名称', max_length=256, help_text="文件/文件夹名")
    key = models.CharField(verbose_name='文件储存在COS中的KEY', max_length=128, null=True, blank=True)
    file_size = models.IntegerField(verbose_name='文件大小/m', null=True, blank=True)
    file_path = models.CharField(verbose_name='文件路径', max_length=255, null=True,
                                 blank=True)  # https://桶.cos.ap-chengdu/....

    parent = models.ForeignKey(verbose_name='父级目录', to='self', related_name='child', null=True, blank=True, on_delete=models.CASCADE)

    update_user = models.ForeignKey(verbose_name='最近更新者', to='UserInfo', on_delete=models.CASCADE)
    update_datetime = models.DateTimeField(verbose_name='更新时间', auto_now=True)



class project_people(models.Model):
    project_id = models.ForeignKey(verbose_name="项目名", to="project", on_delete=models.CASCADE)
    user = models.ForeignKey(verbose_name="参与者", to="UserInfo", on_delete=models.CASCADE)
    start = models.BooleanField(verbose_name="星标", default=False)
    create_time = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)


class trade(models.Model):
    # state_choice = (
    #     (1, '已支付'),
    #     (2, '未支付')
    # )
    state = models.BooleanField(verbose_name="交易状态")
    order = models.CharField(verbose_name="订单号", max_length=64, unique=True)
    user_id = models.ForeignKey(verbose_name="用户名", to="UserInfo", on_delete=models.CASCADE)
    prices = models.ForeignKey(verbose_name="价格", to="fees", on_delete=models.CASCADE)
    true_pay = models.IntegerField(verbose_name="实际付款")
    start_time = models.DateTimeField(verbose_name="开始时间", null=True, blank=True)
    end_time = models.DateTimeField(verbose_name="结束时间", null=True, blank=True)
    quantity = models.IntegerField(verbose_name="数量/年")
    """django默认把当前时间添加到该条数据中， 不用自己添加"""
    create_time = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)


class Issues(models.Model):
    """ 问题 """
    project = models.ForeignKey(verbose_name='项目', to='project', on_delete=models.CASCADE)
    issues_type = models.ForeignKey(verbose_name='问题类型', to='IssuesType', on_delete=models.CASCADE)
    module = models.ForeignKey(verbose_name='模块', to='Module', null=True, blank=True, on_delete=models.CASCADE)

    subject = models.CharField(verbose_name='问题名称', max_length=80)
    desc = models.TextField(verbose_name='问题描述')
    priority_choices = (
        ("danger", "高"),
        ("warning", "中"),
        ("success", "低"),
    )
    priority = models.CharField(verbose_name='优先级', max_length=12, choices=priority_choices, default='danger')

    # 新建、处理中、已解决、已忽略、待反馈、已关闭、重新打开
    status_choices = (
        (1, '新建'),
        (2, '处理中'),
        (3, '已解决'),
        (4, '已忽略'),
        (5, '待反馈'),
        (6, '已关闭'),
        (7, '重新打开'),
    )
    status = models.SmallIntegerField(verbose_name='状态', choices=status_choices, default=1)

    assign = models.ForeignKey(verbose_name='指派', to='UserInfo', related_name='task', null=True, blank=True,
                               on_delete=models.CASCADE)
    attention = models.ManyToManyField(verbose_name='关注者', to='UserInfo', related_name='observe', blank=True)

    start_date = models.DateField(verbose_name='开始时间', null=True, blank=True)
    end_date = models.DateField(verbose_name='结束时间', null=True, blank=True)
    mode_choices = (
        (1, '公开模式'),
        (2, '隐私模式'),
    )
    mode = models.SmallIntegerField(verbose_name='模式', choices=mode_choices, default=1)

    parent = models.ForeignKey(verbose_name='父问题', to='self', related_name='child', null=True, blank=True,
                               on_delete=models.SET_NULL)

    creator = models.ForeignKey(verbose_name='创建者', to='UserInfo', related_name='create_problems',
                                on_delete=models.CASCADE)

    create_datetime = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    latest_update_datetime = models.DateTimeField(verbose_name='最后更新时间', auto_now=True)

    def __str__(self):
        return self.subject


class Module(models.Model):
    """ 模块（里程碑）"""
    project = models.ForeignKey(verbose_name='项目', to='project', on_delete=models.CASCADE)
    title = models.CharField(verbose_name='模块名称', max_length=32)

    def __str__(self):
        return self.title


class IssuesType(models.Model):
    """ 问题类型 例如：任务、修正 """
    type_list = ['任务', '修正']
    title = models.CharField(verbose_name='类型名称', max_length=32)
    project = models.ForeignKey(verbose_name='项目', to='project', on_delete=models.CASCADE)

    def __str__(self):
        return self.title


class IssuesReply(models.Model):
    """ 问题回复"""

    reply_type_choices = (
        (1, '修改记录'),
        (2, '回复')
    )
    reply_type = models.IntegerField(verbose_name='类型', choices=reply_type_choices)

    issues = models.ForeignKey(verbose_name='问题', to='Issues', on_delete=models.CASCADE)
    content = models.TextField(verbose_name='描述')
    creator = models.ForeignKey(verbose_name='创建者', to='UserInfo', related_name='create_reply', on_delete=models.CASCADE)
    create_datetime = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)

    reply = models.ForeignKey(verbose_name='回复', to='self', null=True, blank=True, on_delete=models.CASCADE)


class ProjectInvite(models.Model):
    """ 项目邀请码 """
    project = models.ForeignKey(verbose_name='项目', to='project', on_delete=models.CASCADE)
    code = models.CharField(verbose_name='邀请码', max_length=64, unique=True)
    use_count = models.PositiveIntegerField(verbose_name='已邀请数量', default=0)
    period_choices = (
        (30, '30分钟'),
        (60, '1小时'),
        (300, '5小时'),
        (1440, '24小时'),
    )
    period = models.IntegerField(verbose_name='有效期', choices=period_choices, default=1440)
    create_datetime = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    creator = models.ForeignKey(verbose_name='创建者', to='UserInfo', related_name='create_invite', on_delete=models.CASCADE)