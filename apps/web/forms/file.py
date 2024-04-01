from django import forms
from apps.web import models
from apps.web.forms import boot_form
from utlis.tencent.cos_qqq import check_file


class FileCreateForm(boot_form.boot_form, forms.ModelForm):
    class Meta:
        model = models.FileRepository
        fields = ['name']


class FileModelForm(boot_form.boot_form, forms.ModelForm):
    etag = forms.CharField(label='ETag')


    class Meta:
        model = models.FileRepository
        exclude = ['project', 'file_type', 'update_user', 'update_datetime']

    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request

    def clean_file_path(self):
        return "https://{}".format(self.cleaned_data['file_path'])


    # def clean_etag(self):
    #     """获取etag和文件名 通过文件名去cos获取文件信息"""
    #     print("xxxxxxxxxx", self.cleaned_data)
    #     key = self.cleaned_data['key']
    #     print("kkk", key)
    #     etag = self.cleaned_data['etag']
    #     if not key or not etag:
    #         return self.cleaned_data
    #     """通过etag校验数据是否合法"""
    #     from qcloud_cos.cos_exception import CosServiceError
    #     """SDK的功能， 向cos校验文件是否合法"""
    #     try:
    #         result = check_file(self.request.tracer.project.bucket, self.request.tracer.project.region, key)
    #     except CosServiceError as e:
    #         self.add_error("key", '文件不存在')
    #         return self.cleaned_data
    #     cos_etag = result.get('Etag')
    #     if cos_etag != etag:
    #         self.add_error("etag", 'etag错误')
    #         return self.cleaned_data
    #     return self.cleaned_data
    #


