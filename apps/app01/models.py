from django.db import models

# Create your models here.
class UserInfo(models.Model):
    name = models.CharField(verbose_name="用户名", max_length= 16)
    email = models.EmailField(verbose_name="邮箱", max_length=32)
    phone = models.CharField(verbose_name="手机号", max_length= 12)
    pwd = models.CharField(verbose_name="密码", max_length=32)