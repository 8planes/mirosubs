from django import forms
from targetter.models import MessageConfig
from targetter import OS_CHOICES, BROWSER_CHOICES

class MessageConfigForm(forms.ModelForm):
    os = forms.MultipleChoiceField(choices=OS_CHOICES, required=False)
    browser = forms.MultipleChoiceField(choices=BROWSER_CHOICES, required=False)
    
    class Meta:
        model = MessageConfig
        exclude = ('os', 'browser')
    
    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance', None)

        if instance:
            initial = kwargs.get('initial', {})
            if instance.os:
                initial['os'] = map(int, instance.os.split(','))
            if instance.browser:
                initial['browser'] = map(int, instance.browser.split(','))
            kwargs['initial'] = initial
            
        super(MessageConfigForm, self).__init__(*args, **kwargs)
    
    def save(self, commit=True):
        os = self.cleaned_data.get('os', [])
        browser = self.cleaned_data.get('browser', [])
        
        obj = super(MessageConfigForm, self).save(False)
        obj.os = ','.join(os)
        obj.browser = ','.join(browser)

        commit and obj.save()
            
        return obj