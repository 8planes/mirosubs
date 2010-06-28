# Universal Subtitles, universalsubtitles.org
# 
# Copyright (C) 2010 Participatory Culture Foundation
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
# 
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see 
# http://www.gnu.org/licenses/agpl-3.0.html.

from django import forms
from auth.models import CustomUser as User
from django.core.mail import EmailMessage

class SendMessageForm(forms.Form):
    email = forms.EmailField()
    message = forms.CharField()
    user = forms.ModelChoiceField(User.objects)
    
    def send(self, user):
        user = self.cleaned_data.get('user')
        email = self.cleaned_data.get('email')
        headers = {'Reply-To': email}
        username = user.username if user.is_authenticated() else 'anonymous'
        subject = 'Personal message from %s on universalsubtitles.org' % username
        EmailMessage(subject, self.cleaned_data.get('message'), email, \
                     [user.email], headers=headers).send()

    def get_errors(self):
        from django.utils.encoding import force_unicode        
        output = {}
        for key, value in self.errors.items():
            output[key] = '/n'.join([force_unicode(i) for i in value])
        return output
                         
class EditUserForm(forms.ModelForm):
    current_password = forms.CharField(widget=forms.PasswordInput, required=False)
    new_password = forms.CharField(widget=forms.PasswordInput, required=False)
    new_password_verify = forms.CharField(widget=forms.PasswordInput,
                                          required=False,
                                          label='Confirm new password:')

    def __init__(self, *args, **kwargs):
        super(EditUserForm, self).__init__(*args, **kwargs)
        self.fields['email'].required = True
    
    class Meta:
        model = User
        fields = ('email', 'homepage', 'preferred_language', 'picture', 
                  'changes_notification', 'biography')
        
    def clean(self):
        current, new, verify = map(self.cleaned_data.get,
                    ('current_password', 'new_password', 'new_password_verify'))
        if current and not self.instance.check_password(current):
            raise forms.ValidationError('Invalid password.')
        if new and new != verify:
            raise forms.ValidationError('The two passwords did not match.')
        if not self.cleaned_data['picture']:
            del self.cleaned_data['picture']
        return self.cleaned_data
    
    def clean_email(self):
        value = self.cleaned_data['email']
        if value:
            try:
                User.objects.exclude(pk=self.instance.pk).get(email=value)
                raise forms.ValidationError('This email is used already.')
            except User.DoesNotExist:
                pass
        return value
    
    def save(self, commit=True):
        password = self.cleaned_data.get('new_password')
        email = self.cleaned_data.get('email')
        if password:
            self.instance.set_password(password)
        if email:
            self.instance.email = email
            self.instance.save()
        return super(EditUserForm, self).save(commit)
        