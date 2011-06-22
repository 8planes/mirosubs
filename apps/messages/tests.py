# -*- coding: utf-8 -*-
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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see
# http://www.gnu.org/licenses/agpl-3.0.html.

import json

from django.test import TestCase
from apps.auth.models import CustomUser as User
from django.core import mail

from apps.messages.models import Message

class MessageTest(TestCase):

    def setUp(self):
        self.author = User.objects.all()[:1].get()
        self.subject = "Let's talk"
        self.body = "Will you please help me out with Portuguese trans?"
        self.user = User.objects.exclude(pk=self.author.pk)[:1].get()
         
    def _create_message(self, to_user):
        self.message = Message(user=to_user,
                           author=self.author,
                           subject=self.subject,
                           content=self.body)
        self.message.save()

    def test_send_email_to_allowed_user(self):
        self.user.changes_notification = True
        self.user.save()
        assert self.user.is_active and self.user.email
        
        self._create_message(self.user)
        self.assertEqual(len(mail.outbox), 1)

    def test_send_email_to_optout_user(self):
        self.user.changes_notification = False
        self.user.save()
        assert self.user.is_active and self.user.email
                
        self._create_message(self.user)
        self.assertEquals(len(mail.outbox), 0)
