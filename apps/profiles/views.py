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
from profiles.forms import EditUserForm, SendMessageForm, UserLanguageFormset, EditAvatarForm
from django.contrib import messages
from django.utils import simplejson as json
from django.utils.translation import ugettext_lazy as _

@login_required
def remove_avatar(request):
    if request.POST.get('remove'):
        request.user.picture = ''
        request.user.save()
    return HttpResponse(json.dumps({}), "text/javascript")

@login_required
def edit_avatar(request):
    output = {}
    form = EditAvatarForm(request.POST, instance=request.user, files=request.FILES)
    if form.is_valid():
        user = form.save()
        output['url'] =  str(user.avatar())
    else:
        output['error'] = form.get_errors()
    return HttpResponse('<textarea>%s</textarea>'  % json.dumps(output))

@login_required
def my_profile(request):
    if request.method == 'POST':
        form = EditUserForm(request.POST,
                            instance=request.user,
                            files=request.FILES, label_suffix="")
        if form.is_valid():
            form.save()
            form_validated = True
        else:
            form_validated = False
            
        formset = UserLanguageFormset(request.POST, instance=request.user)
        if formset.is_valid() and form_validated:
            formset.save()
            messages.success(request, _('Your profile has been updated.'))
            return redirect('profiles:my_profile')
    else:
        form = EditUserForm(instance=request.user, label_suffix="")
        formset = UserLanguageFormset(instance=request.user)
    context = {
        'form': form,
        'user_info': request.user,
        'formset': formset
    }
    return render_to_response('profiles/edit_profile.html', context,
                              context_instance=RequestContext(request))

def profile(request, user_id=None):
    if user_id:
        try:
            user = User.objects.get(username=user_id)
        except User.DoesNotExist:
            try:
                user = User.objects.get(id=user_id)
            except (User.DoesNotExist, ValueError):
                raise Http404
    else:
        user = request.user
    context = {
        'user_info': user,
        'can_edit': user == request.user
    }
    return render_to_response('profiles/view_profile.html', context,
                                  context_instance=RequestContext(request))            

@login_required
def send_message(request):
    output = dict(success=False)
    form = SendMessageForm(request.user, request.POST)
    if form.is_valid():
        form.send()
        output['success'] = True
    else:
        output['errors'] = form.get_errors()
    return HttpResponse(json.dumps(output), "text/javascript")    