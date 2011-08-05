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
from widget.rpc import Rpc
from datetime import datetime, timedelta
from django.core.management import call_command
from django.core import mail
from apps.videos import metadata_manager 
import re

from widget.tests import create_two_sub_session, RequestMockup

LANGUAGEPAIR_RE = re.compile(r"([a-zA-Z\-]+)_([a-zA-Z\-]+)_(.*)")
LANGUAGE_RE = re.compile(r"S_([a-zA-Z\-]+)")

from apps.teams.tests.teamstestsutils import refresh_obj, reset_solr , rpc
    
from django.core.exceptions import SuspiciousOperation

from apps.teams.moderation_const import SUBJECT_EMAIL_VERSION_REJECTED    
from apps.teams.moderation import  UNMODERATED, APPROVED, WAITING_MODERATION, \
    add_moderation, remove_moderation, approve_version, is_moderated, reject_version
from apps.videos.models import SubtitleVersion, Subtitle, VideoUrl
from apps.teams.forms import EditTeamVideoForm


class BaseTestModeration(TestCase):

    def _create_versions(self, lang, num_versions=1, num_subs=None, user=None):
        versions = []
        lang = refresh_obj(lang)
        for num in xrange(0, num_versions):
            v = SubtitleVersion(language=lang)
            if lang.subtitleversion_set.all().count() > 0:
                v.version_no = lang.subtitleversion_set.all()[0].version_no + 1
            else:

                v.version_no = 1    
            v.datetime_started  = datetime.now()
            v.user = user or self.user or User.objects.all()[0]
            v.save()
            versions.append(v)
            for i in xrange(0,3):
                s = Subtitle(version=v, subtitle_text="%s%s%s" % (lang.pk, v.version_no, i), subtitle_order=i, subtitle_id="%s-%s-"  % (v.pk, i))
                s.save()
        return versions

class TestVideoModerationForm(BaseTestModeration):
    fixtures = ["staging_users.json", "staging_videos.json", "staging_teams.json"]
     
    def setUp(self):
        self.auth = dict(username='admin', password='admin')
        self.team  = Team.objects.all()[0]
        self.video = self.team.videos.all()[0]
        self.user = User.objects.all()[0]
        member = TeamMember(user=self.user, team=self.team, role=TeamMember.ROLE_MANAGER)
        member.save()

    def _login(self):
        self.client.login(**self.auth)

    def test_is_moderated_exists_on_empty(self):
        tv,created = TeamVideo.objects.get_or_create(team=self.team, video=self.video)
        form = EditTeamVideoForm(None,  None, instance=tv, user=self.user)
        field = form.fields.get( "is_moderated", False)
        self.assertTrue(field)
        self.assertEquals(field.initial, False)

    def test_is_moderated_stores_teams(self):
        tv,created = TeamVideo.objects.get_or_create(team=self.team, video=self.video)
        form = EditTeamVideoForm({"is_moderated": True},  None, instance=tv, user=self.user)
        form.save()
        self.video = Video.objects.get(pk=self.video.pk)
        self.assertTrue(self.video.moderated_by)
        self.assertEquals(self.team, self.video.moderated_by)

    def test_is_moderated_unset_removess_teams(self):
        add_moderation(self.video, self.team, self.user)
        tv,created = TeamVideo.objects.get_or_create(team=self.team, video=self.video)
        form = EditTeamVideoForm({"is_moderated": False},  None, instance=tv, user=self.user)
        form.save()
        self.video = Video.objects.get(pk=self.video.pk)
        self.assertFalse(self.video.moderated_by)

    def test_only_one_moderator_per_video(self):
        add_moderation(self.video, self.team, self.user)
        team , created = Team.objects.get_or_create(slug="a", name="a")
        tv, created = TeamVideo.objects.get_or_create(video=self.video, team=team, added_by=self.user)
        form = EditTeamVideoForm(None,  None, instance=tv, user=self.user)
        field = form.fields.get( "is_moderated", False)
        self.assertFalse(field)

    def test_video_moderator_change_in_form(self):
        add_moderation(self.video, self.team, self.user)
        self.assertTrue(is_moderated(self.video))
        team , created = Team.objects.get_or_create(slug="a", name="a")
        tv, created = TeamVideo.objects.get_or_create(video=self.video, team=team, added_by=self.user)
        form = EditTeamVideoForm(None,  None, instance=tv, user=self.user)
        field = form.fields.get( "is_moderated", False)
        moderating_tv =  TeamVideo.objects.get(team=self.team, video=self.video)
        
        form = EditTeamVideoForm({"is_moderated":False},  None, instance=moderating_tv, user=self.user)
        field = form.fields.get( "is_moderated", None)
        self.assertTrue(field is not None)
        if form.is_valid():
            form.save()
        self.assertTrue(form.is_valid())
        self.video = Video.objects.get(pk=self.video.pk)
        self.assertFalse(is_moderated(self.video))
        
class TestBusinessLogic( BaseTestModeration):
    fixtures = ["staging_users.json", "staging_videos.json", "staging_teams.json"]
     
    def setUp(self):
        self.auth = dict(username='admin', password='admin')
        self.team  = Team.objects.all()[0]
        self.video = self.team.videos.all()[0]
        self.user = User.objects.all()[0]

        self.auth_user  = User.objects.get(username= self.auth["username"])

    def _login(self, is_moderator=False):
            if is_moderator:
                o, c = TeamMember.objects.get_or_create(user=self.auth_user, team=self.team)
                o.role=TeamMember.ROLE_MANAGER
                o.save()
            self.client.login(**self.auth)

    def _make_subs(self, lang, num=10):
        v = SubtitleVersion(language=lang, is_forked=False, datetime_started=datetime.now())
        try:
            version_no  = lang.subtitleversion_set.all()[:1].get().version_no + 1
        except SubtitleVersion.DoesNotExist:
            version_no = 0

        v.version_no = version_no
        v.save()
        for x  in xrange(0, num):
            subtitle = Subtitle(
                subtitle_id = str(x),
                subtitle_order = x,
                subtitle_text = "Sub %s for %s" % ( x, lang),
                start_time = x,
                end_time = x + 0.9
            )
            subtitle.save()
        return v
    

    def test_create_moderation_simple(self):
        TeamMember(user=self.user, team=self.team, role=TeamMember.ROLE_MANAGER).save()
        self.assertFalse(self.video.moderated_by)
        add_moderation(self.video, self.team, self.user)
        self.video = Video.objects.get(pk=self.video.pk)
        self.assertEquals(self.video.moderated_by, self.team)

    def test_create_moderation_only_for_members(self):
        member = TeamMember(user=self.user, team=self.team, role=TeamMember.ROLE_MEMBER)
        member.save()
        e = None
        try:
            add_moderation(self.video, self.team, self.user)
                       
        except SuspiciousOperation, e:
            pass
        self.assertTrue(e)
        member.is_manager  = True
        member.save()
        self.assertRaises(SuspiciousOperation, add_moderation, *[self.video, self.team, self.user])
        self._login(is_moderator=True)
        add_moderation (self.video, self.team, self.auth_user)
        self.video = Video.objects.get(pk=self.video.pk)
        self.assertTrue(self.video.moderated_by)

    def test_remove_moderation_simple(self):
        TeamMember(user=self.user, team=self.team, role=TeamMember.ROLE_MANAGER).save()
        self.assertFalse(self.video.moderated_by)
        add_moderation(self.video, self.team, self.user)
        self.video = Video.objects.get(pk=self.video.pk)
        self.assertTrue(self.video.moderated_by)
        remove_moderation(self.video, self.team, self.user)
        self.video = Video.objects.get(pk=self.video.pk)
        self.assertFalse(self.video.moderated_by)

    def test_remove__moderation_only_for_members(self):
        member = TeamMember(user=self.user, team=self.team, role=TeamMember.ROLE_MANAGER)
        member.save()
        add_moderation(self.video, self.team, self.user)
        member.role = TeamMember.ROLE_MEMBER
        member.save()
        e = None
        self.assertRaises(SuspiciousOperation, remove_moderation, *(self.video, self.team, self.user))
        member.role = TeamMember.ROLE_MANAGER
        member.save()
        remove_moderation(self.video, self.team, self.user)
        self.video = Video.objects.get(pk=self.video.pk)
        self.assertFalse(self.video.moderated_by)


    def test_on_adding_we_approve_previsous_versions(self):
        #from apps.testhelpers.views import debug_video
        lang = self.video.subtitle_language()
        
        v1 = self._make_subs(lang, 5)
        self.assertEquals(v1.moderation_status , UNMODERATED)
        member = TeamMember(user=self.user, team=self.team, role=TeamMember.ROLE_MANAGER)
        member.save()
        add_moderation(self.video, self.team, self.user)
        v1 = SubtitleVersion.objects.get(pk=v1.pk)
        self.assertEquals(v1.moderation_status , APPROVED)

    def test_new_version_will_await_moderation(self):
        #from apps.testhelpers.views import debug_video
        lang = self.video.subtitle_language()
        member = TeamMember(user=self.user, team=self.team, role=TeamMember.ROLE_MANAGER)
        member.save()
        v0 = self._make_subs(lang, 5)
        self.assertEquals(v0.moderation_status , UNMODERATED)
        add_moderation(self.video, self.team, self.user)
        v1 = self._create_versions(self.video.subtitle_language(), num_versions=1)[0]
        self.assertEquals(v1.moderation_status , WAITING_MODERATION)


    def test_approval_activity_stream(self):
        member = TeamMember(user=self.user, team=self.team, role=TeamMember.ROLE_MANAGER)
        member.save()
        add_moderation(self.video, self.team, self.user)
        v1 = self._create_versions(self.video.subtitle_language(), num_versions=1)[0]
        count = Action.objects.all().count()
        approve_version(v1, self.team, self.user)
        self.assertEquals(count + 1, Action.objects.all().count())
        act  = Action.objects.all().order_by("-created")[0]
        act.action_type == Action.APPROVE_VERSION


    def test_rejection_activity_stream(self):
        member = TeamMember(user=self.user, team=self.team, role=TeamMember.ROLE_MANAGER)
        member.save()
        add_moderation(self.video, self.team, self.user)
        v1 = self._create_versions(self.video.subtitle_language(), num_versions=1)[0]
        count = Action.objects.all().count()
        reject_version(v1, self.team, self.user)
        self.assertEquals(count + 1, Action.objects.all().count())
        act  = Action.objects.all().order_by("-created")[0]
        act.action_type == Action.REJECT_VERSION
        

class TestModerationViews(BaseTestModeration):
    fixtures = ["staging_users.json", "staging_videos.json", "staging_teams.json", "moderation.json"]
     
    def setUp(self):
        self.auth = dict(username='admin', password='admin')
        self.team  = Team.objects.all()[0]
        self.video = self.team.videos.all()[0]
        l = self.video.subtitle_language()
        l.language = 'en'
        l.save()
        self.user = User.objects.all()[0]
        self.auth_user = User.objects.get(username=self.auth["username"])
        member = TeamMember(user=self.user, team=self.team, role=TeamMember.ROLE_MANAGER)
        member.save()

    def _make_subs(self, lang, num=10):
        version_no = 0
        if lang.subtitleversion_set.all().exists():
            version_no = lang.subtitleversion_set.all()[0].version_no + 1
        v = SubtitleVersion(language=lang, is_forked=False,
                            datetime_started=datetime.now(),
                            user = self.user,
                            version_no=version_no)
        v.save()
        for x  in xrange(0, num):
            subtitle = Subtitle(
                subtitle_id = str(x),
                subtitle_order = x,
                subtitle_text = "vno:%s Sub %s for %s" % ( version_no, x, lang),
                start_time = x,
                end_time = x + 0.9,
                version=v
                
            )
            subtitle.save()
        return v
    

    def _login(self, is_moderator=False):
            if is_moderator:
                o, c = TeamMember.objects.get_or_create(user=self.auth_user, team=self.team)
                o.role=TeamMember.ROLE_MANAGER
                o.save()
            self.client.login(**self.auth)
        
    def _call_rpc_method(self, method_name,  *args, **kwargs):
        request = RequestMockup(self.user)
        return  getattr(rpc, method_name)(request, *args, **kwargs)
    
    def test_moderated_subs_pending_count(self):
        add_moderation(self.video, self.team, self.user)
        lang = self.video.subtitle_language()
        [ self._make_subs(lang, 5) for x in xrange(0, 3)]
        self.assertEquals(self.team.get_pending_moderation().count(), 3)
        lang = SubtitleLanguage(video=self.video, language="pt", title="a")
        lang.save()
        [ self._make_subs(lang, 5) for x in xrange(0, 3)]
        self.assertEquals(self.team.get_pending_moderation().count(), 6)
        # make sure pending count is for only one team
        tv = TeamVideo.objects.exclude(team=self.team).filter(video__moderated_by__isnull=True)[0]
        o, c = TeamMember.objects.get_or_create(user=self.auth_user, team=tv.team)
        o.role=TeamMember.ROLE_MANAGER
        o.save()
        new_team = tv.team
        add_moderation(tv.video, tv.team, self.auth_user)

        lang = SubtitleLanguage(video=tv.video, language="pt", title="a")
        lang.save()
        [ self._make_subs(lang, 5) for x in xrange(0, 3)]
        self.assertEquals(self.team.get_pending_moderation().count(), 6)
        self.assertEquals(tv.team.get_pending_moderation().count(), 3)

    def test_moderated_subs_approve_one(self):
        video = Video.objects.get(pk=4)
        tv = TeamVideo(video=video, team=self.team,added_by=self.user)
        tv.save()
        url = reverse("teams:detail", kwargs={"slug": self.team.slug})
        response = self.client.get(url)
        add_moderation(video, self.team, self.user)
        self._login(is_moderator=True)
        self.client.get("\en\faq")        
        lang = video.subtitle_language()
        [ self._make_subs(lang, 5) for x in xrange(0, 3)]
        self.assertEquals(self.team.get_pending_moderation().count(), 3)
        
        lang = SubtitleLanguage(video=video, language="pt", title="a", standard_language=lang)
        lang.save()
        [ self._make_subs(lang, 5) for x in xrange(0, 3)]
        # we can see the unmoderated sub on the website,
        response = self.client.get(reverse("videos:translation_history", kwargs={
                'video_id':video.video_id,
                'lang':lang.language,
                'lang_id':lang.id
        }))
        versions =  SubtitleVersion.objects.filter(language=lang)
        latest_version =  lang.latest_version(public_only=False) #lang.subtitleversion_set.all()[0]
        
        subs = response.context['last_version'].subtitle_set.all()
        self.assertEquals(latest_version, response.context['last_version'])
        self.assertTrue(subs[0].subtitle_text.startswith("vno:2 Sub 0 "))
        self.assertTrue(len(subs))
        self.assertEquals(self.team.get_pending_moderation().count(), 6)
        versions = self.team.get_pending_moderation()
        version = versions[0]
        # after moderation it should not be visible on the widget
        subs = self._call_rpc_method("fetch_subtitles", lang.video.video_id, lang.pk)
        self.assertFalse(subs)


        url = reverse("moderation:revision-approve", kwargs={
                    "team_id":self.team.id,
                    "version_id":version.pk} )
        response = self.client.post(url, {},follow=True,  HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEquals(response.status_code, 200)
        
        data  =  json.loads(response.content)
        self.assertTrue(data["success"])


        self.team = refresh_obj(self.team)
        self.assertEquals(self.team.get_pending_moderation().count(), 5)
        version = SubtitleVersion.objects.get(pk=version.pk)
        self.assertEquals(version.moderation_status,APPROVED)

        response = self.client.get(reverse("videos:translation_history", kwargs={
                'video_id':video.video_id,
                'lang':lang.language,
                'lang_id':lang.id
        }))
        sub_1 = response.context['last_version'].subtitle_set.all()
        self.assertTrue(len(sub_1))
        widget_res = self._call_rpc_method("fetch_subtitles", version.video.video_id, version.language.pk)
        self.assertTrue(widget_res)
        self.assertTrue(widget_res["subtitles"])
        
        sub = widget_res["subtitles"][0]
        self.assertTrue(sub["text"].startswith("vno:2 Sub 0 "))


    def test_rejection_view_no_message(self):
        from apps.comments.models import Comment
        tv = self.team.teamvideo_set.all()[0]
        add_moderation(tv.video, tv.team, self.user)
        self.assertEquals(tv.team.get_pending_moderation().count() , 0)
        self.version = self._create_versions( tv.video.subtitle_language(), num_versions=1)[0]
        self.reject_url = reverse("moderation:revision-reject", kwargs={
                "team_id": self.team.pk,
                "version_id": self.version.pk,
        })
        # reject first without messge, no notification nor comments should be save

        response = self.client.post(self.reject_url, {}, HTTP_X_REQUESTED_WITH= "XMLHttpRequest", follow=True)
        res_data = json.loads(response.content)
        # not logged in! cannot moderate this
        self.assertFalse(res_data["success"])
        self._login(is_moderator=True)
        prev_comments_count = Comment.objects.all().count()

        self.version = self._create_versions( tv.video.subtitle_language(), num_versions=1)[0]
        self.reject_url = reverse("moderation:revision-reject", kwargs={
                "team_id": self.team.pk,
                "version_id": self.version.pk,
        })
        response = json.loads(self.client.post(self.reject_url, {}, HTTP_X_REQUESTED_WITH= "XMLHttpRequest", follow=True).content)
        self.assertTrue(response["success"])
        
        self.assertEquals ( Comment.objects.all().count() , prev_comments_count)


        version2 = self._create_versions(self.video.subtitle_language() , num_versions=1)[0]
        self.reject_url = reverse("moderation:revision-reject", kwargs={
                "team_id": tv.team.pk,
                "version_id": version2.pk,
        })
        response = self.client.post(self.reject_url, {"message": "bad version"}, HTTP_X_REQUESTED_WITH= "XMLHttpRequest", follow=True)
        data = json.loads(response.content)
        self.assertTrue(data["success"])
        self.assertEquals ( Comment.objects.all().count() , prev_comments_count + 1)

                          
        
        followers = set(self.video.notification_list(self.auth_user))
        followers.update(self.version.language.notification_list(self.auth_user))
        self.assertEquals (len(mail.outbox), len(followers))
        email = mail.outbox[0]
        subject = SUBJECT_EMAIL_VERSION_REJECTED  % self.video.title_display()
        self.assertEqual(email.subject, subject)

    def test_moderated_subs_reject_one(self):
        url = reverse("teams:detail", kwargs={"slug": self.team.slug})
        response = self.client.get(url)
        add_moderation(self.video, self.team, self.user)
        self._login(is_moderator=True)
        self.client.get("\en\faq")        
        lang = self.video.subtitle_language()
        [ self._make_subs(lang, 5) for x in xrange(0, 3)]
        self.assertEquals(self.team.get_pending_moderation().count(), 3)
        lang = SubtitleLanguage(video=self.video, language="pt", title="a")
        lang.save()
        [ self._make_subs(lang, 5) for x in xrange(0, 3)]
        self.assertEquals(self.team.get_pending_moderation().count(), 6)
        versions = self.team.get_pending_moderation()
        version = versions[0]

        url = reverse("moderation:revision-approve", kwargs={
                    "team_id":self.team.id,
                    "version_id":version.pk})
        response = self.client.post(url, {},follow=True)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(self.team.get_pending_moderation().count(), 5)
        version = SubtitleVersion.objects.get(pk=version.pk)
        self.assertEquals(version.moderation_status,APPROVED)

class TestSubtitleVersions(BaseTestModeration):
    fixtures = ["staging_users.json", "staging_videos.json", "staging_teams.json"]
     
    def setUp(self):
        self.auth = dict(username='admin', password='admin')
        self.team  = Team.objects.all()[0]
        self.video = self.team.videos.all()[0]
        self.user = User.objects.all()[0]
        member = TeamMember(user=self.user, team=self.team, role=TeamMember.ROLE_MANAGER)
        member.save()
        self.user2 = User.objects.exclude(pk=self.user.pk)[0]
        
    def _make_subs(self, lang, num=10):
        version_no = 0
        if lang.subtitleversion_set.all().exists():
            version_no = lang.subtitleversion_set.all()[0].version_no + 1
        v = SubtitleVersion(language=lang, is_forked=False,
                            datetime_started=datetime.now(),
                            version_no=version_no)
        v.save()
        for x  in xrange(0, num):
            subtitle = Subtitle(
                subtitle_id = str(x),
                subtitle_order = x,
                subtitle_text = "Sub %s for %s" % ( x, lang),
                start_time = x,
                end_time = x + 0.9
                
            )
            subtitle.save()
        return v
    
    def _login(self):
        self.client.login(**self.auth)

    
    def test_moderated_subs_visibility(self):
        lang = self.video.subtitle_language()
        add_moderation(self.video, self.team, self.user)
        v0 = self._make_subs(lang, 5)
        self.assertEquals(v0.moderation_status , WAITING_MODERATION)
        approve_version(v0, self.team, self.user)
        v0 = SubtitleVersion.objects.get(pk=v0.pk)
        self.assertEquals(v0.moderation_status , APPROVED)
        lang = SubtitleLanguage.objects.get(pk=lang.pk)

        self.assertEquals(lang.version().pk, v0.pk)
        
        v1 = self._make_subs(lang, 5)
        lang = SubtitleLanguage.objects.get(pk=lang.pk)
        self.assertEquals(v1.moderation_status , WAITING_MODERATION)
        lang = SubtitleLanguage.objects.get(pk=lang.pk)
        version = lang.version()
        self.assertEquals(version, v0)
        approve_version(v1, self.team, self.user)
        v1 = SubtitleVersion.objects.get(pk=v1.pk)
        self.assertEquals(v1.moderation_status , APPROVED)
        lang = SubtitleLanguage.objects.get(pk=lang.pk)
        version = lang.version()
        self.assertEquals(version, v1)

    def _get_widget_moderation_status(self, video_url):

        request = RequestMockup(self.user)
        request.user = self.user
        res = rpc.show_widget(request, video_url, is_remote=False)
        return res
    
    def test_cache_has_right_value(self):
        video_url = VideoUrl.objects.all()[0]
        tv = TeamVideo(video=video_url.video, team=self.team,added_by=self.user)
        tv.save()
        res =  self._get_widget_moderation_status(video_url.url)
        self.assertFalse(res["is_moderated"])
        video, created = Video.get_or_create_for_url(video_url.url)
        add_moderation(video, self.team, self.user)
        res =  self._get_widget_moderation_status(video_url.url)
        self.assertTrue(res["is_moderated"])

    def test_contribuitors_do_bypass_moderation(self):
        lang = self.video.subtitle_language()
        member, created = TeamMember.objects.get_or_create(user=self.user, team=self.team)
        member.role=TeamMember.ROLE_MANAGER
        member.save()
        add_moderation(self.video, self.team, self.user)
        joe_doe = User(username="joedoe", password="joedoe", email="joedow@example.com")
        joe_doe.save()
        joe_member, c = TeamMember.objects.get_or_create(user=joe_doe, team=self.team)
        joe_member.save()
        v0 = self._create_versions(lang, 1, user=joe_doe)[0]
        self.assertEquals(v0.moderation_status,WAITING_MODERATION)
        joe_member.promote_to_contributor()
        joe_doe = refresh_obj(joe_doe)

        self.assertTrue(self.team.is_contributor(joe_doe, authenticated=False))
        v1 = self._create_versions(lang, 1, user=joe_doe)[0]
        metadata_manager.update_metadata(self.video.pk)
        v1 = refresh_obj(v1)
        self.assertEquals(v1.moderation_status, APPROVED)
        

class TestDashboard(TestSubtitleVersions, BaseTestModeration):
    def test_pending_count(self):
        self.assertEquals(self.team.get_pending_moderation().count() , 0)
        tv = self.team.teamvideo_set.all()[0]
        add_moderation(tv.video, tv.team, self.user)
        self.assertEquals(self.team.get_pending_moderation().count() , 0)
        self._create_versions( tv.video.subtitle_language(), num_versions=2)
        self.assertEquals(self.team.get_pending_moderation().count(), 2)

class TestRemoval(TestSubtitleVersions, BaseTestModeration):
    def test_pending_count_after_removal(self):
        
        tv = self.team.teamvideo_set.all()[0]
        add_moderation(tv.video, tv.team, self.user)
        self.assertEquals(tv.team.get_pending_moderation().count() , 0)
        self._create_versions( tv.video.subtitle_language(), num_versions=2)
        self.assertEquals(tv.team.get_pending_moderation().count(), 2)
        remove_moderation(tv.video, tv.team, self.user)
        self.assertEquals(tv.team.get_pending_moderation().count(), 0)

    def test_last_version_never_rejected(self):
        tv = self.team.teamvideo_set.all()[0]
        add_moderation(tv.video, tv.team, self.user)
        self.assertEquals(tv.team.get_pending_moderation().count() , 0)
        versions = self._create_versions( tv.video.subtitle_language(), num_versions=2)
        approve_version(versions[1], tv.team, self.user)
        remove_moderation(tv.video, tv.team, self.user)
        version = refresh_obj(versions[0])
        self.assertEquals(version.moderation_status , UNMODERATED)
        version = refresh_obj(versions[1])
        self.assertEquals(version.moderation_status , UNMODERATED)

    def test_on_unmoderation_rejected_never_last(self):
       tv = self.team.teamvideo_set.all()[0]
       add_moderation(tv.video, tv.team, self.user)
       self.assertEquals(tv.team.get_pending_moderation().count() , 0)
       versions = self._create_versions( tv.video.subtitle_language(), num_versions=2)
       v0_subs_text = versions[0].subtitles()[0].text
       v1_subs_text = versions[1].subtitles()[0].text
       approve_version(versions[0], tv.team, self.user)
       num_versions = SubtitleVersion.objects.filter(language__video=tv.video).count()
       reject_version(versions[1], tv.team, self.user, None, self.user2)
       # we should roll back
       self.assertEquals(SubtitleVersion.objects.filter(language__video=tv.video).count(),num_versions +1)
       self.assertEquals( tv.video.subtitle_language().latest_version(), versions[0])
       remove_moderation(tv.video, tv.team, self.user)
       # the last one must be v0 -> the one approved
       self.assertEquals(tv.video.subtitle_language().latest_version().subtitles()[0].text , v0_subs_text)
       
class TestTeamTemplateTags(BaseTestModeration):

    def test_render_belongs_to_list(self):
        # FIXME implement test
        return

