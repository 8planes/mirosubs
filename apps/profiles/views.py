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

from auth.models import CustomUser as User
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponse
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from profiles.forms import EditUserForm, SendMessageForm
from django.contrib import messages
from django.utils import simplejson as json

@login_required
def my_profile(request):
    return profile(request)

def profile(request, user_id=None):
    if user_id:
        try:
            user = User.objects.get(username=user_id)
        except User.DoesNotExist:
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                raise Http404
    else:
        user = request.user
    context = {
        'user_info': user
    }

    if request.user == user:
        if request.method == 'POST':
            form = EditUserForm(request.POST,
                                instance=request.user,
                                files=request.FILES, label_suffix="")
            if form.is_valid():
                form.save()
                messages.success(request, 'Your profile has been updated.')
                return redirect('profiles:my_profile')
        else:
            form = EditUserForm(instance=request.user, label_suffix="")
        context['form'] = form
        return render_to_response('profiles/edit_profile.html', context,
                                  context_instance=RequestContext(request))
    else:
        return render_to_response('profiles/view_profile.html', context,
                                  context_instance=RequestContext(request))
            

def send_message(request):
    output = dict(success=False)
    form = SendMessageForm(request.POST)
    if form.is_valid():
        form.send(request.user)
        output['success'] = True
    else:
        output['errors'] = form.get_errors()
    return HttpResponse(json.dumps(output), "text/javascript")    