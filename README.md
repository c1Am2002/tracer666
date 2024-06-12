1.这个项目用到了腾讯云的对象存储系统， 请提前准备好相应的账号
2.你需要在根目录下创建一个文件名为local_setting.py的python文件， 写下如下内容
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "", # 安装redis的主机的 IP 和 端口
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "CONNECTION_POOL_KWARGS": {
                "max_connections": 1000,
                "encoding": 'utf-8'
            },
            # "PASSWORD": "" # redis密码
        }
    }
}

secret_key = 你的cos对象存储系统的key
3.修改cos_qqq文件中的secret_id为你自己的id
4.在终端输入指令pip install -r packs.txt下载项目所需库， 其中某些库依赖c++编译器， 请提前准备
5.在终端依次输入 python manage.py makemigrations， python manage.py migrate自动在数据库创建数据表
