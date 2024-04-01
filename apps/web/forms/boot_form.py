class boot_form(object):
    """保持样式工整"""
    def __init__(self,  *args, **kwargs):
        super().__init__(*args, **kwargs)
        not_user = ['color',]
        for name ,field in self.fields.items():
            if name in not_user:
                continue
            old_class = field.widget.attrs.get('class', "")
            field.widget.attrs['class'] = '{} form-control'.format(old_class)