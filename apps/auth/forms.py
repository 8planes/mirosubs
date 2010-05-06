from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms

class CustomUserCreationForm(UserCreationForm):
    
    class Meta:
        model = User
        fields = ("username", "email")
        
    def __init__(self, *args, **kwargs):
        super(CustomUserCreationForm, self).__init__(*args, **kwargs)
        self.fields['email'].required = True
        
    def _get_unique_checks(self):
        #add email field validate like unique
        unique_checks, date_checks = super(CustomUserCreationForm, self)._get_unique_checks()
        unique_checks.append(('email',))
        return unique_checks, date_checks