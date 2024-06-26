# Generated by Django 3.2.23 on 2024-03-25 12:35

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0007_auto_20240324_1916'),
    ]

    operations = [
        migrations.CreateModel(
            name='IssuesReply',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reply_type', models.IntegerField(choices=[(1, '修改记录'), (2, '回复')], verbose_name='类型')),
                ('content', models.TextField(verbose_name='描述')),
                ('create_datetime', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('creator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='create_reply', to='web.userinfo', verbose_name='创建者')),
                ('issues', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='web.issues', verbose_name='问题')),
                ('reply', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='web.issuesreply', verbose_name='回复')),
            ],
        ),
    ]
