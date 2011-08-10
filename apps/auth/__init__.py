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

# We make sure we always have an anonymous user that can be used
# as 'placeholder' for models instead of having them be nullable
# requires a ANONYMOUS_USER_ID on settings (which defaults to -1)

from django.db.models import signals
from django.conf import settings
from django.contrib.auth.models import User
from apps.auth.models import CustomUser
from apps.auth import models as custom_auth_app



def create_anonymous_user(sender, **kwargs):
    """
    Creates anonymous User instance with id from settings.
    """
    try:
        User.objects.get(pk=settings.ANONYMOUS_USER_ID)
    except User.DoesNotExist:
        u = User.objects.create(pk=guardian_settings.ANONYMOUS_USER_ID,
            username='AnonymousUser')
        CustomUser.objects.get_or_create(pk=u.pk, user_ptr=u)

signals.post_syncdb.connect(create_anonymous_user, sender=custom_auth_app,
    dispatch_uid="auth.management.create_anonymous_user")
