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
from teams.models import Team, TeamMember
from django.utils.translation import ugettext_lazy as _

class CreateTeamForm(forms.ModelForm):
    
    class Meta:
        model = Team
        exclude = ('videos', 'users', 'applicants', 'invited')
    
    def save(self, user):
        team = super(CreateTeamForm, self).save()
        TeamMember(team=team, user=user, is_manager=True).save()
        return team
    
class EditTeamForm(forms.ModelForm):
    
    class Meta:
        model = Team
        exclude = ('videos', 'users', 'applicants', 'invited') 
        
    def clean(self):
        if not self.cleaned_data['logo']:
            del self.cleaned_data['logo']
        return self.cleaned_data           