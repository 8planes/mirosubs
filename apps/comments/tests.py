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

import json, datetime

from django.test import TestCase
from django.core.urlresolvers import reverse
from django.contrib.sites.models import Site
from django.contrib.contenttypes.models import ContentType

from videos.models import Video, Action, VIDEO_TYPE_YOUTUBE, UserTestResult, \
    SubtitleLanguage, VideoUrl, SubtitleVersion
from apps.auth.models import CustomUser as User

from django.core import mail
from apps.comments.models import Comment
from apps.comments.notifications import  notify_comment_by_email, SUBJECT_EMAIL_VIDEO_COMMENTED
from django.db.models import ObjectDoesNotExist 


class CommentEmailTests(TestCase):

    fixtures = ['test.json']

    def setUp(self):
        self.user = User.objects.all()[0]
        self.video = Video.objects.all()[0]

        self.auth = dict(username='admin', password='admin')
        self.logged_user = User.objects.get(username=self.auth['username'])
        l = self.video.subtitle_language()
        l.language = "en"
        l.save()
        comment = Comment(content_object=self.video)
        comment.user = self.logged_user
        comment.content = "testme"
        comment.submit_date = datetime.datetime.now()
        comment.save()
        self.comment = comment

    def _create_followers(self, video, num_followers):
        for x in xrange(0,num_followers):
            u = User(username="%s@example.lcom" %x, email="%s@example.com" % x)
            u.save()
            video.followers.add(u)
            
    def _post_comment_for(self, obj):
        self.client.login(**self.auth)
        data = {
          "content": "hi from tests",
          'content_type' : ContentType.objects.get_for_model(obj).pk,
          'object_pk':obj.pk

          }
        response = self.client.post(reverse("comments:post"), data)
        self.assertEqual(response.status_code, 200)
        return response


    def test_universal_urls(self):
        from localeurl.utils import universal_url
        domain= Site.objects.get_current().domain
        vid = self.video.video_id
        self.assertEqual("http://%s/videos/%s/info/" % (domain, vid) , universal_url( "videos:video", kwargs={"video_id":vid} ))
        self.assertEqual("http://%s/videos/%s/info/" % (domain, vid) , universal_url( "videos:video", args=(vid,) ))
                    
    def test_simple_email(self):
        num_followers = 5
        self._create_followers(self.video, num_followers)
        notify_comment_by_email(self.comment)
        self.assertEqual(len(mail.outbox), num_followers)
        email = mail.outbox[0]
        self.assertEqual(email.subject, SUBJECT_EMAIL_VIDEO_COMMENTED  % (self.comment.user.username,
                                                                          self.video.title_display()))
        return None

    def test_comment_view_for_video(self):
        num_followers = 2
        self._create_followers(self.video, num_followers)
        response = self._post_comment_for(self.video)
        followers = set(self.video.notification_list(self.logged_user))
        self.assertEqual(len(mail.outbox), len(followers))
        email = mail.outbox[0]
        self.assertEqual(email.subject, SUBJECT_EMAIL_VIDEO_COMMENTED  % (self.comment.user.username,
                                                                          self.video.title_display()))

    def test_comment_view_for_language(self):
        num_followers = 2
        self._create_followers(self.video, num_followers)
        lang = self.video.subtitle_language()
        response = self._post_comment_for(lang)
        followers = set(self.video.notification_list(self.logged_user))
        followers.update(lang.notification_list(self.logged_user))
        self.assertEqual(len(mail.outbox), len(followers))
        email = mail.outbox[0]
        self.assertEqual(email.subject, SUBJECT_EMAIL_VIDEO_COMMENTED  % (self.comment.user.username,
                                                                          self.video.title_display()))
        
