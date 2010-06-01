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
from videos.models import Video, UserTestResult
from django.core.mail import EmailMessage, send_mail
from django.conf import settings
import re

class UserTestResultForm(forms.ModelForm):
    
    class Meta:
        model = UserTestResult
        exclude = ('browser',)
        
    def save(self, request):
        obj = super(UserTestResultForm, self).save(False)
        obj.browser = request.META.get('HTTP_USER_AGENT', 'empty HTTP_USER_AGENT')
        obj.save()
        return obj

class VideoForm(forms.ModelForm):
    class Meta:
        model = Video
        fields = ('video_url',)

class FeedbackForm(forms.Form):
    email = forms.EmailField(required=False)
    message = forms.CharField(widget=forms.Textarea())
    
    def send(self, request):
        email = self.cleaned_data['email']
        message = self.cleaned_data['message']
        user_agent_data = 'User agent: %s' % request.META.get('HTTP_USER_AGENT')
        message = '%s\n\n%s' % (message, user_agent_data)
        headers = {'Reply-To': email} if email else None
        
        EmailMessage(settings.FEEDBACK_SUBJECT, message, email, \
                     [settings.FEEDBACK_EMAIL], headers=headers).send()
                     
    def get_errors(self):
        from django.utils.encoding import force_unicode        
        output = {}
        for key, value in self.errors.items():
            output[key] = '/n'.join([force_unicode(i) for i in value])
        return output

email_list_re = re.compile(
    r"""^(([-!#$%&'*+/=?^_`{}|~0-9A-Z]+(\.[-!#$%&'*+/=?^_`{}|~0-9A-Z]+)*|^"([\001-\010\013\014\016-\037!#-\[\]-\177]|\\[\001-011\013\014\016-\177])*")@(?:[A-Z0-9]+(?:-*[A-Z0-9]+)*\.)+[A-Z]{2,6},)+$""", re.IGNORECASE)

class EmailListField(forms.RegexField):
    default_error_messages = {
        'invalid': u'Enter valid e-mail addresses separated by commas.',
    }
    
    def __init__(self, max_length=None, min_length=None, *args, **kwargs):
        super(EmailListField, self).__init__(email_list_re, max_length, min_length, *args, **kwargs)
    
    def clean(self, value):
        if value:
            value = value and value.endswith(',') and value or value+','
        return super(EmailListField, self).clean(value)
    
class EmailFriendForm(forms.Form):
    from_email = forms.EmailField(label='From')
    to_emails = EmailListField(label='To')
    subject = forms.CharField()
    message = forms.CharField(widget=forms.Textarea())
    
    def send(self):
        subject = self.cleaned_data['subject']
        message = self.cleaned_data['message']
        from_email = self.cleaned_data['from_email']
        to_emails = self.cleaned_data['to_emails'].strip(',').split(',')
        send_mail(subject, message, from_email, to_emails)