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
from auth.models import CustomUser as User, UserLanguage
from django.core.mail import EmailMessage
from django.forms.models import inlineformset_factory, BaseInlineFormSet, BaseModelFormSet
from django.forms.formsets import BaseFormSet
from django.utils.translation import ugettext_lazy as _
from utils.validators import MaxFileSizeValidator
from django.conf import settings
from utils.forms import AjaxForm
from utils.translation import get_languages_list, get_simple_languages_list
from django.utils import simplejson as json
from utils.translation import set_user_languages_to_cookie

class SelectLanguageForm(forms.Form):
    language1 = forms.ChoiceField(choices=(), required=False)
    language2 = forms.ChoiceField(choices=(), required=False)
    language3 = forms.ChoiceField(choices=(), required=False)
    language4 = forms.ChoiceField(choices=(), required=False)
    language5 = forms.ChoiceField(choices=(), required=False)
    language6 = forms.ChoiceField(choices=(), required=False)
    language7 = forms.ChoiceField(choices=(), required=False)
    language8 = forms.ChoiceField(choices=(), required=False)
    language9 = forms.ChoiceField(choices=(), required=False)

    def __init__(self, *args, **kwrags):
        super(SelectLanguageForm, self).__init__(*args, **kwrags)
        lc = get_languages_list(True)
        
        for i in xrange(1, 10):
            self.fields['language%s' % i].choices = lc
    
    def save(self, user, response=None):
        data = self.cleaned_data
        
        languages = []
        
        for i in xrange(1, 10):
            if data.get('language%s' % i): languages.append(data.get('language%s' % i))
        
        if user.is_authenticated():
            UserLanguage.objects.filter(user=user).delete()
            for l in languages:
                UserLanguage.objects.get_or_create(user=user, language=l)
        else:
            if not response is None:
                set_user_languages_to_cookie(response, languages)
            else:
                return languages
    
class UserLanguageForm(forms.ModelForm):
    
    class Meta:
        model = UserLanguage
        # TODO #request subtitles: Remove this after implementing request notifications
        exclude = ('follow_requests',)
        
    def __init__(self, *args, **kwrags):
        super(UserLanguageForm, self).__init__(*args, **kwrags)
        self.fields['language'].choices = get_languages_list(True)

class UserLanguagelineFormSet(BaseInlineFormSet):

    def _construct_form(self, i, **kwargs):
        try:
            return super(UserLanguagelineFormSet, self). _construct_form(i, **kwargs)
        except (IndexError, ValueError):
            return BaseFormSet._construct_form(self, i, **kwargs)

UserLanguageFormset = inlineformset_factory(User, UserLanguage, UserLanguageForm, UserLanguagelineFormSet, extra=1)

class SendMessageForm(forms.Form):
    email = forms.EmailField()
    message = forms.CharField()
    user = forms.ModelChoiceField(User.objects)
    
    def __init__(self, sender, *args, **kwargs):
        self.sender = sender
        super(SendMessageForm, self).__init__(*args, **kwargs)
    
    def clean_user(self):
        user = self.cleaned_data['user']
        if not user.email:
            raise forms.ValidationError(_(u'This user has not email'))
        return user
    
    def clean(self):
        if not self.sender.is_authenticated():
            raise forms.ValidationError(_(u'You are not authenticated.'))
        return self.cleaned_data
    
    def send(self):
        user = self.cleaned_data.get('user')
        email = self.cleaned_data.get('email')
        headers = {'Reply-To': email}
        subject = _('Personal message from %(sender)s on universalsubtitles.org') % {'sender': self.sender.username}
        EmailMessage(subject, self.cleaned_data.get('message'), email, \
                     [user.email], headers=headers).send()

    def get_errors(self):
        from django.utils.encoding import force_unicode        
        output = {}
        for key, value in self.errors.items():
            output[key] = '/n'.join([force_unicode(i) for i in value])
        return output

class EditAvatarForm(forms.ModelForm, AjaxForm):
    picture = forms.ImageField(validators=[MaxFileSizeValidator(settings.AVATAR_MAX_SIZE)], required=False)

    class Meta:
        model = User
        fields = ('picture',)

    def clean(self):
        if 'picture' in self.cleaned_data and not self.cleaned_data.get('picture'):
            del self.cleaned_data['picture']
        return self.cleaned_data

class EditUserEmailForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(EditUserEmailForm, self).__init__(*args, **kwargs)
        self.fields['email'].required = True
    
    class Meta:
        model = User
        fields = ('email',)    
                         
class EditUserForm(forms.ModelForm):
    current_password = forms.CharField(widget=forms.PasswordInput, required=False)
    new_password = forms.CharField(widget=forms.PasswordInput, required=False)
    new_password_verify = forms.CharField(widget=forms.PasswordInput,
                                          required=False,
                                          label=_(u'Confirm new password:'))
    
    def __init__(self, *args, **kwargs):
        super(EditUserForm, self).__init__(*args, **kwargs)
        self.fields['email'].required = True
        self.fields['preferred_language'].choices = get_languages_list(True)
        
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'homepage', 'preferred_language', 
                  'changes_notification', 'biography', 'new_message_notification', 'follow_new_video')
        
    def clean(self):
        self.cleaned_data = super(EditUserForm, self).clean()
        current, new, verify = map(self.cleaned_data.get,
                    ('current_password', 'new_password', 'new_password_verify'))
        if current and not self.instance.check_password(current):
            raise forms.ValidationError(_(u'Invalid password.'))
        if new and new != verify:
            raise forms.ValidationError(_(u'The two passwords did not match.'))
        return self.cleaned_data
    
    def save(self, commit=True):
        password = self.cleaned_data.get('new_password')
        email = self.cleaned_data.get('email')
        if password:
            self.instance.set_password(password)
        if email:
            self.instance.email = email
            self.instance.save()
        return super(EditUserForm, self).save(commit)
        
