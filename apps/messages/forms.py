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

#  Based on: http://www.djangosnippets.org/snippets/73/
#
#  Modified by Sean Reifschneider to be smarter about surrounding page
#  link context.  For usage documentation see:
#
#     http://www.tummy.com/Community/Articles/django-pagination/

from django import forms
from messages.models import Message
from auth.models import CustomUser as User, UserLanguage
from utils.forms import AjaxForm
from django.utils.translation import ugettext_lazy as _, ugettext
from teams.models import Team
from django.db.models import Count
from utils.translation import get_simple_languages_list

class SendMessageForm(forms.ModelForm, AjaxForm):
    
    class Meta:
        model = Message
        fields = ('user', 'subject', 'content')
        
    def __init__(self, author, *args, **kwargs):
        self.author = author
        super(SendMessageForm, self).__init__(*args, **kwargs)
        self.fields['user'].widget = forms.HiddenInput()
        self.fields['user'].queryset = User.objects.exclude(pk=author.pk)
        
    def clean(self):
        if not self.author.is_authenticated():
            raise forms.ValidationError(_(u'You should be authenticated to write messages'))
        return self.cleaned_data
        
    def save(self, commit=True):
        obj = super(SendMessageForm, self).save(False)
        obj.author = self.author
        commit and obj.save()
        return obj
    
class SendTeamMessageForm(forms.ModelForm, AjaxForm):
    team = forms.ModelChoiceField(queryset=Team.objects.all(), widget = forms.HiddenInput())
    languages = forms.MultipleChoiceField(label=_('Only send to speakers of...'), 
                  widget=forms.CheckboxSelectMultiple(attrs={'class': 'langs'}),
                  required=False)    
    
    class Meta:
        model = Message
        fields = ('subject', 'content')

    def __init__(self, author, *args, **kwargs):
        self.author = author
        if 'team' in kwargs.get('initial', {}):
            self.team = kwargs['initial']['team']
            kwargs['initial']['team'] = self.team.pk
        else:
            self.team = None

        super(SendTeamMessageForm, self).__init__(*args, **kwargs)

        if self.team:
            self.fields['languages'].choices = self._get_language_choise(self.team)
        else:
            self.fields['languages'].choices = get_simple_languages_list()
    
    def _get_language_choise(self, team):
        choices = []
        
        languages = dict(get_simple_languages_list())
        
        langs = UserLanguage.objects.exclude(user=self.author) \
            .filter(user__teams=team).values_list('language') \
            .annotate(Count('language'))
        
        for lang, count in langs:
            name = '%s(%s)' % (languages[lang], count)
            choices.append((lang, name))
        
        return choices
        
    def clean_team(self):
        team = self.cleaned_data['team']
        
        if not team.is_manager(self.author):
            raise forms.ValidationError(_(u'You are not manager of this team.'))
        
        return team
    
    def clean(self):
        if not self.author.is_authenticated():
            raise forms.ValidationError(_(u'You should be authenticated to write messages'))
        return self.cleaned_data
    
    def save(self):
        messages = []
        
        team = self.cleaned_data['team']
        languages = self.cleaned_data['languages']

        members = team.users.exclude(pk=self.author.pk)
        
        if languages:
            members = members.filter(userlanguage__language__in=languages).distinct()

        for user in members:
            message = Message(user=user)
            message.author = self.author
            message.content = self.cleaned_data['content']
            message.subject = self.cleaned_data['subject']
            message.object = team
            message.save()
            messages.append(message)
            
        return messages
    
class TeamAdminPageMessageForm(forms.ModelForm):
    
    class Meta:
        model = Message
        fields = ('subject', 'content')
    
    def send_to_teams(self, team_ids, author):
        subject = self.cleaned_data['subject']
        content = self.cleaned_data['content']
        content = u''.join([content, '\n\n', ugettext('This message is from site administrator.')])
        users = User.objects.filter(teams__in=team_ids).exclude(pk=author.pk)
        for user in users:
            m = Message(author=author, user=user)
            m.subject = subject
            m.content = content
            m.save()
        return users.count()
