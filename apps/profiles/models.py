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

from django.db import models
from django.contrib.auth.models import User
import registration.signals
from django.contrib.auth import login, authenticate

# The registration module is only being used to check emails. These two
#functions ensure that the user is active immediately after registering and that
# profile.valid_email reflects whether the user has verified her email.
def register_user(sender, user, request, **kwargs):
    if not user:
        return
    user.is_active = True
    user.save()
    u = authenticate(username=request.POST.get('username'),
                     password=request.POST.get('password1'))
    if u is not None:
        login(request, u)
registration.signals.user_registered.connect(register_user)

def activate_user(sender, user, request, **kwargs):
    if not user:
        return
    user.valid_email = True
    user.save()
registration.signals.user_activated.connect(activate_user)