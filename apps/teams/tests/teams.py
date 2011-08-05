# -*- coding: utf-8 -*-

import os
import json

from django.test import TestCase
from django.core.urlresolvers import reverse
from os import path

from django.conf import settings
from apps.teams.models import Team, Invite, TeamVideo, \
    Application, TeamMember, TeamVideoLanguage
from messages.models import Message
from videos.models import Video, VIDEO_TYPE_YOUTUBE, SubtitleLanguage, Action
from django.db.models import ObjectDoesNotExist
from auth.models import CustomUser as User
from django.contrib.contenttypes.models import ContentType
from apps.teams import tasks

from datetime import datetime, timedelta
from django.core.management import call_command
from django.core import mail
from apps.videos import metadata_manager 
import re


from widget.tests import create_two_sub_session, RequestMockup

LANGUAGEPAIR_RE = re.compile(r"([a-zA-Z\-]+)_([a-zA-Z\-]+)_(.*)")
LANGUAGE_RE = re.compile(r"S_([a-zA-Z\-]+)")

from apps.teams.tests.teamstestsutils import refresh_obj, reset_solr, rpc

from django.conf import settings


class TestNotification(TestCase):
    
    fixtures = ["test.json"]
    
    def setUp(self):
        self.team = Team(name='test', slug='test')
        self.team.save()
        
        self.user = User.objects.all()[:1].get()
        self.user.is_active = True
        self.user.changes_notification = True
        self.user.email = 'test@test.com'
        self.user.save()
        
        self.tm = TeamMember(team=self.team, user=self.user)
        self.tm.save()

        v1 = Video.objects.all()[:1].get()
        self.tv1 = TeamVideo(team=self.team, video=v1, added_by=self.user)
        self.tv1.save()
        
        v2 = Video.objects.exclude(pk=v1.pk)[:1].get()
        self.tv2 = TeamVideo(team=self.team, video=v2, added_by=self.user)
        self.tv2.save()
        
    def test_new_team_video_notification(self):
        #check initial data
        self.assertEqual(self.team.teamvideo_set.count(), 2)
        self.assertEqual(self.team.users.count(), 1)

        
        #mockup for send_templated_email to test context of email
        import utils
        
        send_templated_email = utils.send_templated_email
        
        def send_templated_email_mockup(to, subject, body_template, body_dict, *args, **kwargs):
            send_templated_email_mockup.context = body_dict
            send_templated_email(to, subject, body_template, body_dict, *args, **kwargs)
        
        utils.send_templated_email = send_templated_email_mockup        
        reload(tasks)
        
        #test notification about two new videos
        TeamVideo.objects.filter(pk__in=[self.tv1.pk, self.tv2.pk]).update(created=datetime.today())
        self.assertEqual(TeamVideo.objects.filter(created__gt=self.team.last_notification_time).count(), 2)
        mail.outbox = []
        tasks.add_videos_notification.delay()
        self.team = Team.objects.get(pk=self.team.pk)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, [self.user.email])
        self.assertEqual(len(send_templated_email_mockup.context['team_videos']), 2)
        
        #test if user turn off notification
        self.user.is_active = False
        self.user.save()
        mail.outbox = []
        tasks.add_videos_notification.delay()
        self.team = Team.objects.get(pk=self.team.pk)
        self.assertEqual(len(mail.outbox), 0)
        
        self.user.is_active = True
        self.user.changes_notification = False
        self.user.save()
        mail.outbox = []
        tasks.add_videos_notification.delay()
        self.team = Team.objects.get(pk=self.team.pk)
        self.assertEqual(len(mail.outbox), 0)        

        self.user.changes_notification = True
        self.user.save()
        self.tm.changes_notification = False
        self.tm.save()
        mail.outbox = []
        tasks.add_videos_notification.delay()
        self.team = Team.objects.get(pk=self.team.pk)
        self.assertEqual(len(mail.outbox), 0)    

        self.tm.changes_notification = True
        self.tm.save()
        
        #test notification if one video is new
        created_date = self.team.last_notification_time + timedelta(seconds=10)
        TeamVideo.objects.filter(pk=self.tv1.pk).update(created=created_date)
        
        self.assertEqual(TeamVideo.objects.filter(created__gt=self.team.last_notification_time).count(), 1)
        mail.outbox = []
        tasks.add_videos_notification.delay()
        self.team = Team.objects.get(pk=self.team.pk)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(len(send_templated_email_mockup.context['team_videos']), 1)
        self.assertEqual(send_templated_email_mockup.context['team_videos'][0], self.tv1)

        #test notification if all videos are already old
        created_date = self.team.last_notification_time - timedelta(seconds=10)
        TeamVideo.objects.filter(team=self.team).update(created=created_date)        
        self.assertEqual(TeamVideo.objects.filter(created__gt=self.team.last_notification_time).count(), 0)
        mail.outbox = []
        tasks.add_videos_notification.delay()
        self.team = Team.objects.get(pk=self.team.pk)
        self.assertEqual(len(mail.outbox), 0)
        
class TestTasks(TestCase):
    
    fixtures = ["staging_users.json", "staging_videos.json", "staging_teams.json"]
    
    def setUp(self):
        self.tv = TeamVideo.objects.all()[0]
        self.sl = SubtitleLanguage.objects.exclude(language='')[0]
        self.team = Team.objects.all()[0]
        tv = TeamVideo(team=self.team, video=self.sl.video, added_by=self.team.users.all()[:1].get())
        tv.save()

class TeamDetailMetadataTest(TestCase):
    fixtures = ["staging_users.json", "staging_videos.json", "staging_teams.json"]
    
    def setUp(self):
        self.auth = {
            "username": u"admin",
            "password": u"admin"
        }
        self.user = User.objects.get(username=self.auth["username"])

    def test_update_lp_no_dependent(self):
        tv = TeamVideo.objects.get(id=2)
        # this video starts with no languages.
        self.assertEquals(0, len(tv.searchable_language_pairs()))
        sl = SubtitleLanguage(
            language='en',
            is_original=True,
            is_forked=False,
            is_complete=False,
            video=tv.video)
        sl.save()
        tv = TeamVideo.objects.get(id=2)
        self.assertEquals(0, len(tv.searchable_language_pairs()))
        sl = tv.video.subtitle_language('en')
        sl.is_complete = True
        sl.save()
        tv = TeamVideo.objects.get(id=2)
        lps = tv.searchable_language_pairs()
        self.assertEquals(len(settings.ALL_LANGUAGES) - 1, len(lps))
        # we expect each string to end in "_0" to indicate zero completion.
        for lp in lps:
            self.assertEquals("0", LANGUAGEPAIR_RE.match(lp).group(3))

    def test_update_lp_with_dep(self):
        tv = TeamVideo.objects.get(id=2)
        sl = SubtitleLanguage(
            language='en',
            is_original=True,
            is_forked=False,
            is_complete=True,
            video=tv.video)
        sl.save()
        dl = SubtitleLanguage(
            language='es',
            is_original=False,
            is_forked=False,
            percent_done=40,
            standard_language=sl,
            video=tv.video)
        dl.save()
        tv = TeamVideo.objects.get(id=2)
        lps = tv.searchable_language_pairs()
        self.assertEquals(len(settings.ALL_LANGUAGES) * 2 - 3, len(lps))
        for lp in lps:
            match = LANGUAGEPAIR_RE.match(lp)
            if match.group(1) == 'en':
                if match.group(2) == 'es':
                    self.assertEquals('M', match.group(3))
                else:
                    self.assertEquals('0', match.group(3))
            elif match.group(1) == 'es':
                self.assertEquals('0', match.group(3))

    def test_update_lp_for_sl(self):
        tv = TeamVideo.objects.get(id=2)
        sl = SubtitleLanguage(
            language='en',
            is_original=True,
            is_forked=False,
            is_complete=True,
            video=tv.video)
        sl.save()
        dl = SubtitleLanguage(
            language='es',
            is_original=False,
            is_forked=False,
            percent_done=40,
            standard_language=sl,
            video=tv.video)
        dl.save()
        tv = TeamVideo.objects.get(id=2)
        dl = SubtitleLanguage.objects.get(id=dl.id)
        dl.percent_done = 50
        dl.save()
        lps = tv.searchable_language_pairs()
        self.assertEquals(len(settings.ALL_LANGUAGES) * 2 - 3, len(lps))
        for lp in lps:
            match = LANGUAGEPAIR_RE.match(lp)
            if match.group(1) == 'en':
                if match.group(2) == 'es':
                    self.assertEquals("M", match.group(3))
                else:
                    self.assertEquals("0", match.group(3))
            elif match.group(1) == 'es':
                self.assertEquals("0", match.group(3))

    def test_update_sl(self):
        tv = TeamVideo.objects.get(id=2)
        sublang = SubtitleLanguage(
            language='en',
            is_original=True,
            is_forked=False,
            is_complete=False,
            video=tv.video)
        sublang.save()
        sls = tv.searchable_languages()
        self.assertEquals(len(settings.ALL_LANGUAGES), len(sls))
        sublang = SubtitleLanguage.objects.get(id=sublang.id)
        sublang.is_complete = True
        sublang.save()
        tv = TeamVideo.objects.get(id=2)
        sls =  tv.searchable_languages()
        self.assertEquals(len(settings.ALL_LANGUAGES) - 1, len(sls))

class TeamsTest(TestCase):
    
    fixtures = ["staging_users.json", "staging_videos.json", "staging_teams.json"]
    
    def setUp(self):
        self.auth = {
            "username": u"admin",
            "password": u"admin"
        }
        self.user = User.objects.get(username=self.auth["username"])
        reset_solr()


    def _add_team_video(self, team, language, video_url):
        mail.outbox = []
        data = {
            "description": u"",
            "language": language,
            "title": u"",
            "video_url": video_url,
            "thumbnail": u"",
        }
        old_count = TeamVideo.objects.count()
        old_video_count = Video.objects.count()
        
        url = reverse("teams:add_video", kwargs={"slug": team.slug})
        response = self.client.post(url, data)
        new_count = TeamVideo.objects.count()
        self.assertEqual(old_count+1, new_count)
        
        if Video.objects.count() > old_video_count:
            created_video = Video.objects.order_by('-created')[0]
            self.assertEqual(self.user, created_video.user)
        
    def _set_my_languages(self, *args):
        from auth.models import UserLanguage
        for ul in self.user.userlanguage_set.all():
            ul.delete()
        for lang in args:
            ul = UserLanguage(
                user=self.user,
                language=lang)
            ul.save()
        self.user = User.objects.get(id=self.user.id)

    def _create_new_team_video(self):
        self.client.login(**self.auth)
        
        response = self.client.get(reverse("teams:create"))
        
        data = {
            "description": u"",
            "video_url": u"",
            "membership_policy": u"4",
            "video_policy": u"1",
            "logo": u"",
            "slug": u"new-team",
            "name": u"New team"
        }

        response = self.client.post(reverse("teams:create"), data)
        self.assertEqual(response.status_code, 302)

        team = Team.objects.get(slug=data['slug'])

        self._add_team_video(team, u'en', u"http://videos.mozilla.org/firefox/3.5/switch/switch.ogv")
        
        tv = TeamVideo.objects.order_by('-id')[0]
        
        result = tasks.update_one_team_video.delay(tv.id)
        
        if result.failed():
            self.fail(result.traceback)

        return team, tv

    def _make_data(self, video_id, lang):
        
        return {
            'language': lang,
            'video': video_id,
            'subtitles': open(os.path.join(settings.PROJECT_ROOT, "apps", 'videos', 'fixtures' ,'test.srt'))
            }

    def _tv_search_record_list(self, team):
        url = reverse("teams:detail", kwargs={"slug": team.slug})
        response = self.client.get(url)
        return response.context['team_video_md_list']

    def _complete_search_record_list(self, team):
        url = reverse("teams:completed_videos", kwargs={"slug": team.slug})
        response = self.client.get(url)
        return response.context['team_video_list']
    
    def test_add_video(self):
        self.client.login(**self.auth)
        
        team = Team.objects.get(pk=1)
        TeamMember.objects.get_or_create(user=self.user, team=team)
        
        self.assertTrue(team.users.count() > 1)
        
        for tm in team.members.all():
            tm.changes_notification = True
            tm.save()
            tm.user.is_active = True
            tm.user.changes_notification = True
            tm.user.save()
        
        self._add_team_video(team, u'en', u"http://videos.mozilla.org/firefox/3.5/switch/switch.ogv")
    
    def test_team_video_delete(self):
        #this test can fail only on MySQL
        team = Team.objects.get(pk=1)
        tv = team.teamvideo_set.exclude(video__subtitlelanguage__language='')[:1].get()
        TeamVideoLanguage.update(tv)
        self.assertNotEqual(tv.languages.count(), 0)
        tv.delete()
        try:
            TeamVideo.objects.get(pk=tv.pk)
            self.fail()
        except TeamVideo.DoesNotExist:
            pass

    def test_complete_contents(self):
        request = RequestMockup(User.objects.all()[0])
        create_two_sub_session(request, completed=True)

        team, new_team_video = self._create_new_team_video()
        en = new_team_video.video.subtitle_language()
        en.is_complete = True
        en.save()
        video = Video.objects.get(id=en.video.id)
        self.assertEqual(True, video.is_complete)

        reset_solr()

        search_record_list = self._complete_search_record_list(team)
        self.assertEqual(1, len(search_record_list))
        search_record = search_record_list[0]
        self.assertEqual(1, len(search_record.video_completed_langs))
        self.assertEqual('en', search_record.video_completed_langs[0])

    def test_detail_contents_after_edit(self):
        # make sure edits show up in search result from solr
        self.client.login(**self.auth)
        team = Team.objects.get(pk=1)
        tv = team.teamvideo_set.get(pk=1)
        tv.title = ''
        tv.description = ''
        tv.save()
        data = {
            "languages-MAX_NUM_FORMS": u"",
            "languages-INITIAL_FORMS": u"0",
            "title": u"change title",
            "languages-0-language": u"el",
            "languages-0-id": u"",
            "languages-TOTAL_FORMS": u"1",
            "languages-0-completed": u"on",
            "thumbnail": u"",
            "description": u"and descriptionnn"
        }
        url = reverse("teams:team_video", kwargs={"team_video_pk": tv.pk})
        response = self.client.post(url, data)
        self.assertRedirects(response, reverse("teams:team_video", kwargs={"team_video_pk": tv.pk}))
        tv = team.teamvideo_set.get(pk=1)
        team_video_search_records = self._tv_search_record_list(team)
        
        for tv in team_video_search_records:
            if tv.title == 'change title':
                break
        self.assertEquals('and descriptionnn', tv.description)

    def test_detail_contents_after_remove(self):
        # make sure removals show up in search result from solr
        self.client.login(**self.auth)
        team = Team.objects.get(pk=1)
        num_team_videos = len(self._tv_search_record_list(team))

        tv = team.teamvideo_set.get(pk=1)
        url = reverse("teams:remove_video", kwargs={"team_video_pk": tv.pk})
        self.client.post(url)

        self.assertEquals(num_team_videos - 1, len(self._tv_search_record_list(team)))

    def test_detail_contents(self):
        team, new_team_video = self._create_new_team_video()
        self.assertEqual(1, new_team_video.video.subtitlelanguage_set.count())

        reset_solr()

        # The video should be in the list. 
        record_list = self._tv_search_record_list(team)
        self.assertEqual(1, len(record_list))
        self.assertEqual(new_team_video.video.video_id, record_list[0].video_id)

    def test_detail_contents_original_subs(self):
        team, new_team_video = self._create_new_team_video()

        # upload some subs to the new video. make sure it still appears.
        data = self._make_data(new_team_video.video.id, 'en')
        response = self.client.post(reverse('videos:upload_subtitles'), data)

        reset_solr()

        url = reverse("teams:detail", kwargs={"slug": team.slug})
        response = self.client.get(url)

        # The video should be in the list.
        self.assertEqual(1, len(response.context['team_video_md_list']))

        # but we should see no "no work" message
        self.assertTrue('allow_noone_language' not in response.context or \
                            not response.context['allow_noone_language'])

    def test_detail_contents_unrelated_video(self):
        team, new_team_video = self._create_new_team_video()
        en = new_team_video.video.subtitle_language()
        en.is_complete = True
        en.save()
        self._set_my_languages('en', 'ru')
        # now add a Russian video with no subtitles.
        self._add_team_video(
            team, u'ru',
            u'http://upload.wikimedia.org/wikipedia/commons/6/61/CollateralMurder.ogv')

        reset_solr()

        team = Team.objects.get(id=team.id)

        self.assertEqual(2, team.teamvideo_set.count())

        # both videos should be in the list
        search_record_list = self._tv_search_record_list(team)
        self.assertEqual(2, len(search_record_list))

        # but the one with en subs should be first, since we can translate it into russian.
        self.assertEqual('en', search_record_list[0].original_language)

    def test_one_tvl(self):
        team, new_team_video = self._create_new_team_video()
        reset_solr()
        self._set_my_languages('ko')
        url = reverse("teams:detail", kwargs={"slug": team.slug})
        response = self.client.get(url)
        self.assertEqual(1, len(response.context['team_video_md_list']))

    def test_no_dupes_without_buttons(self):
        team, new_team_video = self._create_new_team_video()
        self._set_my_languages('ko', 'en')

        self.client.post(
            reverse('videos:upload_subtitles'), 
            self._make_data(new_team_video.video.id, 'en'))

        self.client.post(
            reverse('videos:upload_subtitles'), 
            self._make_data(new_team_video.video.id, 'es'))

        url = reverse("teams:detail", kwargs={"slug": team.slug})
        response = self.client.get(url)
        self.assertEqual(1, len(response.context['team_video_md_list']))
    
    def test_team_create_with_video(self):
        self.client.login(**self.auth)
        
        response = self.client.get(reverse("teams:create"))
        self.failUnlessEqual(response.status_code, 200)
        
        data = {
            "description": u"",
            "video_url": u"http://www.youtube.com/watch?v=OFaWxcH6I9E",
            "membership_policy": u"4",
            "video_policy": u"1",
            "logo": u"",
            "slug": u"new-team-with-video",
            "name": u"New team with video"
        }
        response = self.client.post(reverse("teams:create"), data)
        self.failUnlessEqual(response.status_code, 302)
        team = Team.objects.get(slug=data['slug'])
        self.assertTrue(team.video)
        self.assertEqual(team.video.user, self.user)
        self.assertTrue(team.video.title)
        
    def test_views(self):
        self.client.login(**self.auth)
        
        #------- create ----------
        response = self.client.get(reverse("teams:create"))
        self.failUnlessEqual(response.status_code, 200)
        
        data = {
            "description": u"",
            "video_url": u"",
            "membership_policy": u"4",
            "video_policy": u"1",
            "logo": u"",
            "slug": u"new-team",
            "name": u"New team"
        }
        response = self.client.post(reverse("teams:create"), data)
        self.failUnlessEqual(response.status_code, 302)
        team = Team.objects.get(slug=data['slug'])

        #---------- index -------------
        response = self.client.get(reverse("teams:index"))
        self.failUnlessEqual(response.status_code, 200) 
               
        response = self.client.get(reverse("teams:index"), {'q': 'vol'})
        self.failUnlessEqual(response.status_code, 200)
        
        data = {
            "q": u"vol",
            "o": u"date"
        }
        response = self.client.get(reverse("teams:index"), data)
        self.failUnlessEqual(response.status_code, 200)

        response = self.client.get(reverse("teams:index"), {'o': 'my'})
        self.failUnlessEqual(response.status_code, 200)
                
        #---------- edit ------------
        url = reverse("teams:edit", kwargs={"slug": team.slug})
        response = self.client.get(url)

        self.failUnlessEqual(response.status_code, 200)
        
        data = {
            "logo": open(path.join(settings.MEDIA_ROOT, "test/71600102.jpg"), "rb")
        }
        url = reverse("teams:edit_logo", kwargs={"slug": team.slug})
        response = self.client.post(url, data)
        self.failUnlessEqual(response.status_code, 200)
        team = Team.objects.get(pk=team.pk)
        self.assertTrue(team.logo)
        
        data = {
            "name": u"New team",
            "video_url": u"http://www.youtube.com/watch?v=tGsHDUdw8As",
            "membership_policy": u"4",
            "video_policy": u"1",
            "description": u"",
            "logo": open(path.join(settings.MEDIA_ROOT, "test/71600102.jpg"), "rb")
        }
        url = reverse("teams:edit", kwargs={"slug": team.slug})
        response = self.client.post(url, data)
        self.failUnlessEqual(response.status_code, 302)
        video = Video.objects.get(videourl__type=VIDEO_TYPE_YOUTUBE, videourl__videoid='tGsHDUdw8As')
        team = Team.objects.get(pk=team.pk)
        self.assertEqual(team.video, video)
        
        #-------------- edit members ---------------
        url = reverse("teams:edit_members", kwargs={"slug": team.slug})
        response = self.client.get(url)
        self.failUnlessEqual(response.status_code, 200)
        
        #-------------- edit videos -----------------
        url = reverse("teams:edit_videos", kwargs={"slug": team.slug})
        response = self.client.get(url)
        self.failUnlessEqual(response.status_code, 200)

        url = reverse("teams:edit", kwargs={"slug": "volunteer1"})
        response = self.client.get(url)
        self.failUnlessEqual(response.status_code, 404)

        self.client.logout()
        
        url = reverse("teams:edit", kwargs={"slug": "volunteer"})
        response = self.client.get(url)
        self.failUnlessEqual(response.status_code, 302)
        
        self.client.login(**self.auth)
        #-------------- applications ----------------
        url = reverse("teams:applications", kwargs={"slug": team.slug})
        response = self.client.get(url)
        self.failUnlessEqual(response.status_code, 200)
        
        #------------ detail ---------------------
        url = reverse("teams:detail", kwargs={"slug": team.slug})
        response = self.client.get(url)
        self.failUnlessEqual(response.status_code, 200)
        
        url = reverse("teams:detail", kwargs={"slug": team.pk})
        response = self.client.get(url)
        self.failUnlessEqual(response.status_code, 200)
        
        url = reverse("teams:detail", kwargs={"slug": team.slug})
        response = self.client.get(url)
        self.failUnlessEqual(response.status_code, 200)
        
        url = reverse("teams:detail", kwargs={"slug": team.slug})
        response = self.client.get(url, {'q': 'Lions'})
        self.failUnlessEqual(response.status_code, 200)
        
        url = reverse("teams:detail", kwargs={"slug": team.slug})
        response = self.client.get(url, {'q': 'empty result'})
        self.failUnlessEqual(response.status_code, 200)        
        
        #------------ detail members -------------
        
        url = reverse("teams:detail_members", kwargs={"slug": team.slug})
        response = self.client.get(url)
        self.failUnlessEqual(response.status_code, 200)
        
        url = reverse("teams:detail_members", kwargs={"slug": team.slug})
        response = self.client.get(url, {'q': 'test'})
        self.failUnlessEqual(response.status_code, 200)

        #-------------members activity ---------------
        #Deprecated
        #url = reverse("teams:members_actions", kwargs={"slug": team.slug})
        #response = self.client.get(url)
        #self.failUnlessEqual(response.status_code, 200)        
        
        #------------- add video ----------------------
        self.client.login(**self.auth)
        
        data = {
            "languages-MAX_NUM_FORMS": u"",
            "description": u"",
            "language": u"en",
            "title": u"",
            "languages-0-language": u"be",
            "languages-0-id": u"",
            "languages-TOTAL_FORMS": u"1",
            "video_url": u"http://www.youtube.com/watch?v=Hhgfz0zPmH4&feature=grec_index",
            "thumbnail": u"",
            "languages-INITIAL_FORMS": u"0"
        }
        tv_len = team.teamvideo_set.count()
        url = reverse("teams:add_video", kwargs={"slug": team.slug})
        response = self.client.post(url, data)
        self.assertEqual(tv_len+1, team.teamvideo_set.count())
        self.assertRedirects(response, reverse("teams:team_video", kwargs={"team_video_pk": 3}))

        #-------edit team video -----------------
        team = Team.objects.get(pk=1)
        tv = team.teamvideo_set.get(pk=1)
        tv.title = ''
        tv.description = ''
        tv.save()
        data = {
            "languages-MAX_NUM_FORMS": u"",
            "languages-INITIAL_FORMS": u"0",
            "title": u"change title",
            "languages-0-language": u"el",
            "languages-0-id": u"",
            "languages-TOTAL_FORMS": u"1",
            "languages-0-completed": u"on",
            "thumbnail": u"",
            "description": u"and description"
        }
        url = reverse("teams:team_video", kwargs={"team_video_pk": tv.pk})
        response = self.client.post(url, data)
        self.assertRedirects(response, reverse("teams:team_video", kwargs={"team_video_pk": tv.pk}))        
        tv = team.teamvideo_set.get(pk=1)
        self.assertEqual(tv.title, u"change title")
        self.assertEqual(tv.description, u"and description")

        #-----------delete video -------------
        url = reverse("teams:remove_video", kwargs={"team_video_pk": tv.pk})
        response = self.client.post(url)
        self.failUnlessEqual(response.status_code, 200)
        try:
            team.teamvideo_set.get(pk=1)
            self.fail()
        except ObjectDoesNotExist:
            pass
        
        #----------inviting to team-----------
        user2 = User.objects.get(username="alerion")
        TeamMember.objects.filter(user=user2, team=team).delete()
        
        data = {
            "username": user2.username,
            "note": u"asd",
            "team_id": team.pk
        }
        response = self.client.post(reverse("teams:invite"), data)
        self.failUnlessEqual(response.status_code, 200)

        invite = Invite.objects.get(user__username=user2.username, team=team)
        ct = ContentType.objects.get_for_model(Invite)
        Message.objects.filter(object_pk=invite.pk, content_type=ct, user=user2)
        
        members_count = team.members.count()
        
        self.client.login(username = user2.username, password ='alerion')
        url = reverse("teams:accept_invite", kwargs={"invite_pk": invite.pk})
        response = self.client.get(url)
        
        self.assertEqual(members_count+1, team.members.count())
        
        self.client.login(**self.auth)

        url = reverse("teams:edit_members", kwargs={"slug": team.slug})
        response = self.client.get(url)
        self.failUnlessEqual(response.status_code, 200)
 
        data = {
            "ot": u"desc",
            "page": u"1",
            "o": u"username"
        }
        url = reverse("teams:edit_members", kwargs={"slug": team.slug})
        response = self.client.get(url, data)
        self.failUnlessEqual(response.status_code, 200)

        tm,c = TeamMember.objects.get_or_create(user=self.user, team=team)
        tm.promote_to_manager()
        
        
        self.assertFalse(team.is_manager(user2))
        url = reverse("teams:promote_member", kwargs={"user_pk": user2.pk, "slug": team.slug})
        response = self.client.get(url)
        self.assertRedirects(response, reverse("teams:edit_members", kwargs={"slug": team.slug}))

        team = refresh_obj(team)
        self.assertTrue(team.is_manager(user2))
        
        url = reverse("teams:promote_member", kwargs={"user_pk": user2.pk, "slug": team.slug})
        response = self.client.post(url, {"role":TeamMember.ROLE_MEMBER})
        self.assertRedirects(response, reverse("teams:edit_members", kwargs={"slug": team.slug}))
        
        self.assertFalse(team.is_manager(user2))
        
        url = reverse("teams:remove_member", kwargs={"user_pk": user2.pk, "slug": team.slug})
        response = self.client.post(url)
        self.failUnlessEqual(response.status_code, 200)
        
        self.assertFalse(team.is_member(user2))
        
        url = reverse("teams:completed_videos", kwargs={"slug": team.slug})
        response = self.client.post(url)
        self.failUnlessEqual(response.status_code, 200)

        url = reverse("teams:videos_actions", kwargs={"slug": team.slug})
        response = self.client.post(url)
        self.failUnlessEqual(response.status_code, 200)
        
        self.client.login()
        TeamMember.objects.filter(user=self.user, team=team).delete()
        self.assertFalse(team.is_member(self.user))
        url = reverse("teams:join_team", kwargs={"slug": team.slug})
        response = self.client.post(url)
        self.failUnlessEqual(response.status_code, 302)
        self.assertTrue(team.is_member(self.user))
        
    def test_fixes(self):
        url = reverse("teams:detail", kwargs={"slug": 'slug-does-not-exist'})
        response = self.client.get(url)
        self.failUnlessEqual(response.status_code, 404)

from apps.teams.rpc import TeamsApiClass
from utils.rpc import Error
from django.contrib.auth.models import AnonymousUser

class TestJqueryRpc(TestCase):
    
    def setUp(self):
        self.team = Team(name='Test', slug='test')
        self.team.save()
        self.user = User.objects.all()[:1].get()
        self.rpc = TeamsApiClass()
        
    def test_create_application(self):
        response = self.rpc.create_application(self.team.pk, '', AnonymousUser())
        if not isinstance(response, Error):
            self.fail('User should be authenticated')
        #---------------------------------------

        response = self.rpc.create_application(None, '', self.user)
        if not isinstance(response, Error):
            self.fail('Undefined team')
        #---------------------------------------    
        self.team.membership_policy = Team.INVITATION_BY_MANAGER
        self.team.save()
        
        response = self.rpc.create_application(self.team.pk, '', self.user)
        if not isinstance(response, Error):
            self.fail('Team is not opened')
        #---------------------------------------
        self.team.membership_policy = Team.OPEN
        self.team.save()
        
        self.assertFalse(self.team.is_member(self.user))
        
        response = self.rpc.create_application(self.team.pk, '', self.user)
        
        if isinstance(response, Error):
            self.fail(response)
        
        self.assertTrue(self.team.is_member(self.user))
        #---------------------------------------
        response = self.rpc.leave(self.team.pk, self.user)
        
        if not isinstance(response, Error):
            self.fail('You are the only member of team')
        
        other_user = User.objects.exclude(pk=self.user)[:1].get()
        self.rpc.join(self.team.pk, other_user)    
        
        response = self.rpc.leave(self.team.pk, self.user)
        if isinstance(response, Error):
            self.fail(response)
                    
        self.assertFalse(self.team.is_member(self.user))           
        #---------------------------------------
        self.team.membership_policy = Team.APPLICATION
        self.team.save()
        
        self.assertFalse(Application.objects.filter(user=self.user, team=self.team).exists())  
        response = self.rpc.create_application(self.team.pk, '', self.user)

        if isinstance(response, Error):
            self.fail(response)
        
        self.assertFalse(self.team.is_member(self.user))
        self.assertTrue(Application.objects.filter(user=self.user, team=self.team).exists())
        #---------------------------------------
        
    def test_join(self):
        self.team.membership_policy = Team.OPEN
        self.team.save()
        
        self.assertFalse(self.team.is_member(self.user))
        
        response = self.rpc.join(self.team.pk, self.user)
        
        if isinstance(response, Error):
            self.fail(response)
        
        self.assertTrue(self.team.is_member(self.user))            

class TeamsDetailQueryTest(TestCase):
    
    fixtures = ["staging_users.json"]
    
    def setUp(self):
        self.auth = {
            "username": u"admin",
            "password": u"admin"
        }    
        self.user = User.objects.get(username=self.auth["username"])

        self.client.login(**self.auth)
        from apps.testhelpers.views import _create_videos, _create_team_videos
        fixture_path = os.path.join(settings.PROJECT_ROOT, "apps", "videos", "fixtures", "teams-list.json")
        data = json.load(open(fixture_path))
        self.videos = _create_videos(data, [self.user])
        self.team, created = Team.objects.get_or_create(name="test-team", slug="test-team")
        self.tvs = _create_team_videos( self.team, self.videos, [self.user])
        reset_solr()

    def _set_my_languages(self, *args):
        from auth.models import UserLanguage
        for ul in self.user.userlanguage_set.all():
            ul.delete()
        for lang in args:
            ul = UserLanguage(
                user=self.user,
                language=lang)
            ul.save()
        self.user = User.objects.get(id=self.user.id)

    def _debug_videos(self):
        from apps.testhelpers.views import debug_video
        return "\n".join([debug_video(v) for v in self.team.videos.all()])

    def _create_rdm_video(self, i):
        video, created = Video.get_or_create_for_url("http://www.example.com/%s.mp4" % i)
        return video

    def test_multi_query(self):
        team, created = Team.objects.get_or_create(slug='arthur')
        team.videos.all().delete()
        from utils import multi_query_set as mq
        created_tvs = [TeamVideo.objects.get_or_create(team=team, added_by=User.objects.all()[0], video=self._create_rdm_video(x) )[0] for x in xrange(0,20)]
        created_pks = [x.pk for x in created_tvs]
        multi = mq.MultiQuerySet(*[TeamVideo.objects.filter(pk=x) for x in created_pks])
        self.assertTrue([x.pk for x in multi] == created_pks)

    def test_hide_trans_back_to_original_lang(self):
        """
        context https://www.pivotaltracker.com/story/show/12883401
        my languages are english and arabic. video is in arabic, 
        and it has complete translations in english and no arabic subs. 
        qs1 and qs2 must not contain opportunity to translate into arabic.
        """
        user_langs = ["en", "ar"]
        self._set_my_languages(*user_langs)
        qs_list, mqs = self.team.get_videos_for_languages_haystack(user_langs)
        titles = [x.video_title for x in qs_list[0]] if qs_list[0] else []
        titles.extend([x.video_title for x in qs_list[1]] if qs_list[1] else [])
        self.assertFalse("dont-translate-back-to-arabic" in titles)

    def test_lingua_franca_later(self):
        # context https://www.pivotaltracker.com/story/show/12883401
        user_langs = ["en", "ar"]
        self._set_my_languages(*user_langs)
        qs_list, mqs = self.team.get_videos_for_languages_haystack(user_langs)
        titles = [x.video_title for x in qs_list[2]]
        self.assertTrue(titles.index(u'a') < titles.index(u'c'))




