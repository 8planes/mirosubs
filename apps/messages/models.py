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
from django.db import models
from auth.models import CustomUser as User
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.conf import settings

MESSAGE_MAX_LENGTH = getattr(settings,'MESSAGE_MAX_LENGTH', 1000)

class Message(models.Model):
    user = models.ForeignKey(User, related_name='received_messages')
    subject = models.CharField(max_length=255, blank=True)
    content = models.TextField(blank=True, max_length=MESSAGE_MAX_LENGTH)
    author = models.ForeignKey(User, blank=True, null=True, related_name='sent_messages')
    read = models.BooleanField(default=False)    
    created = models.DateTimeField(auto_now_add=True)

    content_type = models.ForeignKey(ContentType, blank=True, null=True,
            related_name="content_type_set_for_%(class)s")
    object_pk = models.TextField('object ID', blank=True, null=True)
    object = generic.GenericForeignKey(ct_field="content_type", fk_field="object_pk")

    class Meta:
        ordering = ['-created']
    
    def __unicode__(self):
        return self.subject or _('<no subject>')
    
    def clean(self):
        from django.core.exceptions import ValidationError
        
        if not self.subject or not self.content or not self.object:
            raise ValidationError(_(u'You should enter subject or message.'))