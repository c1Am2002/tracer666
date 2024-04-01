from apps.web.forms import boot_form
from django import forms
from apps.web import models
class wikimodelform(boot_form.boot_form, forms.ModelForm):
    class Meta:
        model = models.wiki
        fields = ['title', 'text', 'father_id']


    def __init__(self, request,   *args, **kwargs):
        super().__init__(*args, **kwargs)
        total_list = [('', '-------'), ]
        wiki_list = models.wiki.objects.filter(project_id=request.tracer.project).values_list('id', 'title')
        total_list.extend(wiki_list)
        self.fields['father_id'].choices = total_list

