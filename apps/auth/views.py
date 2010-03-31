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

from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login

def login(request):
    redirect_to = request.REQUEST.get(REDIRECT_FIELD_NAME, '')
    return render_login(request, UserCreationForm(), 
                        AuthenticationForm(), redirect_to)

def make_redirect_to(request):
    redirect_to = request.REQUEST.get(REDIRECT_FIELD_NAME, '')
    if not redirect_to or '//' in redirect_to or ' ' in redirect_to:
        return '/'
    else:
        return redirect_to

def create_user(request):
    redirect_to = make_redirect_to(request)
    form = UserCreationForm(request.POST)
    if form.is_valid():
        new_user = form.save()
        user = authenticate(username=new_user.username,
                            password=form.cleaned_data['password1'])
        auth_login(request, user)
        return HttpResponseRedirect(redirect_to)
    else:
        return render_login(request, form, AuthenticationForm(), redirect_to)

def login_post(request):
    redirect_to = make_redirect_to(request)
    form = AuthenticationForm(data=request.POST)
    if form.is_valid():
        auth_login(request, form.get_user())
        if request.session.test_cookie_worked():
            request.session.delete_test_cookie()
        return HttpResponseRedirect(redirect_to)
    else:
        return render_login(request, UserCreationForm(), form, redirect_to)

# Helpers

def render_login(request, user_creation_form, login_form, redirect_to):
    return render_to_response(
        'auth/login.html', {
            'creation_form': user_creation_form,
            'login_form' : login_form,
            REDIRECT_FIELD_NAME: redirect_to,
            }, context_instance=RequestContext(request))
        
