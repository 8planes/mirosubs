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
from django.template.loader import render_to_string
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.contrib.sites.models import Site
from auth.models import CustomUser as User, Awards
from django.conf import settings
from django.db.models.signals import post_save

from localeurl.utils import universal_url
from utils.tasks import send_templated_email_async

COMMENT_MAX_LENGTH = getattr(settings,'COMMENT_MAX_LENGTH', 3000)


class Comment(models.Model):
    content_type = models.ForeignKey(ContentType,
            related_name="content_type_set_for_%(class)s")
    object_pk = models.TextField('object ID')
    content_object = generic.GenericForeignKey(ct_field="content_type", fk_field="object_pk")
    user = models.ForeignKey(User)
    reply_to = models.ForeignKey('self', blank=True, null=True)
    content = models.TextField('comment', max_length=COMMENT_MAX_LENGTH)
    submit_date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ('-submit_date',)
        
    def __unicode__(self):
        return "%s: %s..." % (self.user.__unicode__(), self.content[:50])
    
    @classmethod
    def get_for_object(self, obj):
        if obj.pk:
            ct = ContentType.objects.get_for_model(obj)
            return self.objects.filter(content_type=ct, object_pk=obj.pk).select_related('user')
        else:
            return self.objects.none()
        
post_save.connect(Awards.on_comment_save, Comment)


