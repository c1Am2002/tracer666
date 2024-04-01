from django.forms import RadioSelect
import apps

class colorRadioSelect(RadioSelect):
    # template_name = 'django/forms/widgets/radio.html'
    # option_template_name = 'django/forms/widgets/radio_option.html'

    template_name = 'wieght/color_radio/radio.html'
    option_template_name = 'wieght/color_radio/radio_option.html'
