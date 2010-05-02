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

from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import render_to_response
from django.template import RequestContext
from profiles.forms import EditProfileForm

@login_required
def my_profile(request):
    return profile(request, request.user.username)

def profile(request, user_id):
    try:
        user = User.objects.get(username=user_id)
    except User.DoesNotExist:
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise Http404
    profile = user.get_profile()
    # TODO: get user's activity
    if request.user == user:
        if request.method == 'POST':
            edit_profile_form = EditProfileForm(request.POST,
                                                instance=profile,
                                                files=request.FILES, label_suffix="")
            if edit_profile_form.is_valid():
                edit_profile_form.save()
                request.user.message_set.create(message='Your profile has been updated.')
        else:
            edit_profile_form = EditProfileForm(instance=profile, label_suffix="")
        return render_to_response('profiles/edit_profile.html', locals(),
                                  context_instance=RequestContext(request))
    else:
        return render_to_response('profiles/view_profile.html', locals(),
                                  context_instance=RequestContext(request))
            
