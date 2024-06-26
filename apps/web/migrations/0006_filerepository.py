# Generated by Django 3.2.23 on 2024-03-20 10:34

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0005_auto_20240317_1845'),
    ]

    operations = [
        migrations.CreateModel(
            name='FileRepository',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file_type', models.SmallIntegerField(choices=[(1, '文件'), (2, '文件夹')], verbose_name='类型')),
                ('name', models.CharField(help_text='文件/文件夹名', max_length=32, verbose_name='文件夹名称')),
                ('key', models.CharField(blank=True, max_length=128, null=True, verbose_name='文件储存在COS中的KEY')),
                ('file_size', models.IntegerField(blank=True, null=True, verbose_name='文件大小')),
                ('file_path', models.CharField(blank=True, max_length=255, null=True, verbose_name='文件路径')),
                ('update_datetime', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='child', to='web.filerepository', verbose_name='父级目录')),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='web.project', verbose_name='项目')),
                ('update_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='web.userinfo', verbose_name='最近更新者')),
            ],
        ),
    ]
