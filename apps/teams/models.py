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
from django.utils.translation import ugettext_lazy as _
from videos.models import Video, SubtitleLanguage
from auth.models import CustomUser as User
from utils.amazon import S3EnabledImageField
from django.db.models.signals import post_save
from messages.models import Message
from django.template.loader import render_to_string
from django.conf import settings
from django.http import Http404
from django.contrib.sites.models import Site
from teams.tasks import update_team_video, update_one_team_video, add_video_notification
from apps.videos.models import SubtitleLanguage

ALL_LANGUAGES = [(val, _(name))for val, name in settings.ALL_LANGUAGES]

class TeamManager(models.Manager):
    
    def for_user(self, user):
        if user.is_authenticated():
            return self.get_query_set().filter(models.Q(is_visible=True)| \
                                        models.Q(members__user=user)).distinct()
        else:
            return self.get_query_set().filter(is_visible=True)

class Team(models.Model):
    APPLICATION = 1
    INVITATION_BY_MANAGER = 2
    INVITATION_BY_ALL = 3
    OPEN = 4
    MEMBERSHIP_POLICY_CHOICES = (
        (APPLICATION, _(u'Application')),
        (INVITATION_BY_MANAGER, _(u'Invitation by manager')),
        (INVITATION_BY_ALL, _(u'Invitation by any member')),
        (OPEN, _(u'Open')),
    )
    MEMBER_REMOVE = 1
    MANAGER_REMOVE = 2
    MEMBER_ADD = 3
    VIDEO_POLICY_CHOICES = (
        (MEMBER_REMOVE, _(u'Members can add and remove video')),  #any member can add/delete video
        (MANAGER_REMOVE, _(u'Managers can add and remove video')),    #only managers can add/remove video
        (MEMBER_ADD, _(u'Members can only add videos'))  #members can only add video
    )
    
    name = models.CharField(_(u'name'), max_length=250, unique=True)
    slug = models.SlugField(_(u'slug'), unique=True)
    description = models.TextField(_(u'description'), blank=True, help_text=_('All urls will be converted to links.'))
    
    logo = S3EnabledImageField(verbose_name=_(u'logo'), blank=True, upload_to='teams/logo/')
    membership_policy = models.IntegerField(_(u'membership policy'), choices=MEMBERSHIP_POLICY_CHOICES, default=OPEN)
    video_policy = models.IntegerField(_(u'video policy'), choices=VIDEO_POLICY_CHOICES, default=MEMBER_REMOVE)
    is_visible = models.BooleanField(_(u'publicly Visible?'), default=True)
    videos = models.ManyToManyField(Video, through='TeamVideo',  verbose_name=_('videos'))
    users = models.ManyToManyField(User, through='TeamMember', related_name='teams', verbose_name=_('users'))
    points = models.IntegerField(default=0, editable=False)
    applicants = models.ManyToManyField(User, through='Application', related_name='applicated_teams', verbose_name=_('applicants'))
    invited = models.ManyToManyField(User, through='Invite', verbose_name=_('invited'))
    created = models.DateTimeField(auto_now_add=True)
    highlight = models.BooleanField(default=False)
    video = models.ForeignKey(Video, null=True, blank=True, related_name='intro_for_teams', verbose_name=_(u'Intro Video'))
    application_text = models.TextField(blank=True)
    page_content = models.TextField(_(u'Page content'), blank=True, help_text=_(u'You can use murkdown. This will replace Description.'))
    is_moderated = models.BooleanField(default=False)
    header_html_text = models.TextField(blank=True, default='', help_text=_(u"HTML that appears at the top of the teams page."))
    
    objects = TeamManager()
    
    class Meta:
        ordering = ['-name']
        verbose_name = _(u'Team')
        verbose_name_plural = _(u'Teams')
    
    def __unicode__(self):
        return self.name
    
    def is_open(self):
        return self.membership_policy == self.OPEN
    
    def is_by_application(self):
        return self.membership_policy == self.APPLICATION
    
    @classmethod
    def get(cls, slug, user=None, raise404=True):
        if user:
            qs = cls.objects.for_user(user)
        else:
            qs = cls.objects.filter(is_visible=True)
        try:
            return qs.get(slug=slug)
        except cls.DoesNotExist:
            try:
                return qs.get(pk=int(slug))
            except (cls.DoesNotExist, ValueError):
                pass
            
        if raise404:
            raise Http404       
    
    def logo_thumbnail(self):
        if self.logo:
            return self.logo.thumb_url(100, 100)

    def small_logo_thumbnail(self):
        if self.logo:
            return self.logo.thumb_url(50, 50)
    
    @models.permalink
    def get_absolute_url(self):
        return ('teams:detail', [self.slug])
    
    def get_site_url(self):
        return 'http://%s%s' % (Site.objects.get_current().domain, self.get_absolute_url())
    
    @models.permalink
    def get_edit_url(self):
        return ('teams:edit', [self.slug])
    
    def is_manager(self, user):
        if not user.is_authenticated():
            return False
        return self.members.filter(user=user, is_manager=True).exists()
    
    def is_member(self, user):
        if not user.is_authenticated():
            return False        
        return self.members.filter(user=user).exists()
    
    def can_remove_video(self, user, team_video=None):
        if not user.is_authenticated():
            return False          
        if self.video_policy == self.MANAGER_REMOVE and self.is_manager(user):
            return True
        if self.video_policy == self.MEMBER_REMOVE and self.is_member(user):
            return True
        return False
    
    def can_edit_video(self, user, team_video=None):
        if not user.is_authenticated():
            return False
        return self.can_add_video(user)
    
    def can_add_video(self, user):
        if not user.is_authenticated():
            return False
        if self.video_policy == self.MEMBER_REMOVE and self.is_member(user):
            return True
        return self.is_manager(user)

    def can_invite(self, user):
        if self.membership_policy == self.INVITATION_BY_MANAGER:
            return self.is_manager(user)
        
        return self.is_member(user)
    
    def can_approve_application(self, user):
        return self.is_member(user)
    
    @property
    def member_count(self):
        if not hasattr(self, '_member_count'):
            setattr(self, '_member_count', self.users.count())
        return self._member_count
    
    @property
    def videos_count(self):
        if not hasattr(self, '_videos_count'):
            setattr(self, '_videos_count', self.videos.count())
        return self._videos_count        
    
    @property
    def applications_count(self):
        if not hasattr(self, '_applications_count'):
            setattr(self, '_applications_count', self.applications.count())
        return self._applications_count            

class TeamVideo(models.Model):
    team = models.ForeignKey(Team)
    video = models.ForeignKey(Video)
    title = models.CharField(max_length=2048, blank=True)
    description = models.TextField(blank=True,
        help_text=_(u'Use this space to explain why you or your team need to caption or subtitle this video. Adding a note makes volunteers more likely to help out!'))
    thumbnail = S3EnabledImageField(upload_to='teams/video_thumbnails/', null=True, blank=True, 
        help_text=_(u'We automatically grab thumbnails for certain sites, e.g. Youtube'))
    all_languages = models.BooleanField(_('Need help with all languages'), default=False, 
        help_text=_('If you check this, other languages will not be displayed.'))
    added_by = models.ForeignKey(User)
    completed_languages = models.ManyToManyField(SubtitleLanguage, blank=True)
    
    class Meta:
        unique_together = (('team', 'video'),)
    
    def __unicode__(self):
        return self.title or self.video.__unicode__()

    def save(self, *args, **kwargs):
        created = bool(not self.pk)
        super(TeamVideo, self).save(*args, **kwargs)
        #asynchronous call
        if created:
            update_one_team_video.delay(self.id)
            add_video_notification.delay(self.id)
            
    def can_remove(self, user):
        return self.team.can_remove_video(user, self)
    
    def can_edit(self, user):
        return self.team.can_edit_video(user, self)
    
    def link_to_page(self):
        if self.all_languages:
            return self.video.get_absolute_url()
        return self.video.video_link()
        
    @models.permalink
    def get_absolute_url(self):
        return ('teams:team_video', [self.pk])
    
    def get_thumbnail(self):
        if self.thumbnail:
            return self.thumbnail.thumb_url(100, 100)

        if self.video.thumbnail:
            th = self.video.get_thumbnail()
            if th:
                return th
        
        if self.team.logo:
            return self.team.logo_thumbnail()
        
        return ''

    def _calculate_percent_complete(self, sl0, sl1):
        # maybe move this to Video model in future.
        if not sl0 or not sl0.is_dependable():
            return -1
        if not sl1:
            return 0
        if sl1.is_dependent():
            if sl1.percent_done == 0:
                return 0
            elif sl0.is_dependent():
                l_dep0 = sl0.real_standard_language()
                l_dep1 = sl1.real_standard_language()
                if l_dep0 and l_dep1 and l_dep0.id == l_dep1.id:
                    return sl1.percent_done
                else:
                    return -1
            else:
                l_dep1 = sl1.real_standard_language()
                return sl1.percent_done if \
                    l_dep1 and l_dep1.id == sl0.id else -1
        else:
            sl1_subtitle_count = 0
            latest_version = sl1.latest_version()
            if latest_version:
                sl1_subtitle_count = latest_version.subtitle_set.count()
            return 0 if sl1_subtitle_count == 0 else -1

    def _update_team_video_language_pair(self, lang0, sl0, lang1, sl1):
        percent_complete = self._calculate_percent_complete(sl0, sl1)
        if sl1 is not None:
            tvlps = TeamVideoLanguagePair.objects.filter(
                team_video=self,
                subtitle_language_0=sl0,
                subtitle_language_1=sl1)
        else:
            tvlps = TeamVideoLanguagePair.objects.filter(
                team_video=self,
                subtitle_language_0__language=lang0,
                language_1=lang1)
        tvlp = None if len(tvlps) == 0 else tvlps[0]
        if not tvlp and percent_complete != -1:
            tvlp = TeamVideoLanguagePair(
                team_video=self,
                team=self.team,
                video=self.video,
                language_0=lang0,
                subtitle_language_0=sl0,
                language_1=lang1,
                subtitle_language_1=sl1,
                language_pair='{0}_{1}'.format(lang0, lang1),
                percent_complete=percent_complete)
            tvlp.save()
        elif tvlp and percent_complete != -1:
            tvlp.percent_complete = percent_complete
            tvlp.save()
        elif tvlp and percent_complete == -1:
            tvlp.remove()

    def _update_tvlp_for_languages(self, lang0, lang1, langs):
        sl0_list = langs.get(lang0, [])
        sl1_list = langs.get(lang1, [])
        if len(sl1_list) == 0:
            sl1_list = [None]
        for sl0 in sl0_list:
            for sl1 in sl1_list:
                self._update_team_video_language_pair(lang0, sl0, lang1, sl1)

    def update_team_video_language_pairs(self, lang_code_list=None):
        TeamVideoLanguagePair.objects.filter(team_video=self).delete()
        if lang_code_list is None:
            lang_code_list = [item[0] for item in settings.ALL_LANGUAGES]
        langs = self.video.subtitle_language_dict()
        for lang0, sl0_list in langs.items():
            for lang1 in lang_code_list:
                if lang0 == lang1:
                    continue
                self._update_tvlp_for_languages(lang0, lang1, langs)
                
    def update_team_video_language_pairs_for_sl(self, sl):
        if not sl.language:
            return

        lang_code_list = [item[0] for item in settings.ALL_LANGUAGES]

        TeamVideoLanguagePair.objects.filter(
            team_video=self, subtitle_language_0=sl).delete()
        TeamVideoLanguagePair.objects.filter(
            team_video=self, subtitle_language_1=sl).delete()
        TeamVideoLanguagePair.objects.filter(
            team_video=self, 
            subtitle_language_1=None, 
            language_1=sl.language).delete()

        langs = self.video.subtitle_language_dict()

        for lang in lang_code_list:
            sl1_list = langs.get(lang, [])
            if len(sl1_list) == 0:
                sl1_list = [None]
            for sl1 in sl1_list:
                self._update_team_video_language_pair(sl.language, sl, lang, sl1)
        for sl0 in self.video.subtitlelanguage_set.all():            
            self._update_team_video_language_pair(sl0.language, sl0, sl.language, sl)

class TeamVideoLanguage(models.Model):
    team_video = models.ForeignKey(TeamVideo, related_name='languages')
    video = models.ForeignKey(Video)
    language = models.CharField(max_length=16, choices=ALL_LANGUAGES,  null=False, blank=False, db_index=True)
    subtitle_language = models.ForeignKey(SubtitleLanguage, null=True)
    team = models.ForeignKey(Team)
    is_original = models.BooleanField(default=False, db_index=True)
    forked = models.BooleanField(default=True, db_index=True)
    is_complete = models.BooleanField(default=False, db_index=True)
    percent_done = models.IntegerField(default=0, db_index=True)
    
    class Meta:
        unique_together = (('team_video', 'subtitle_language'),)

    def __unicode__(self):
        return self.get_language_display()

    @classmethod
    def _save_tvl_for_sl(cls, tv, sl):
        tvl = cls(
            team_video=tv,
            video=tv.video,
            language=sl.language,
            subtitle_language=sl,
            team=tv.team,
            is_original=sl.is_original,
            forked=sl.is_forked,
            is_complete=sl.is_complete,
            percent_done=sl.percent_done)
        tvl.save()

    @classmethod
    def _save_tvl_for_l(cls, tv, lang):
        tvl = cls(
            team_video=tv,
            video=tv.video,
            language=lang,
            subtitle_language=None,
            team=tv.team,
            is_original=False,
            forked=True,
            is_complete=False,
            percent_done=0)
        tvl.save()

    @classmethod
    def _update_for_language(cls, tv, language, sublang_dict):
        if language in sublang_dict:
            sublangs = sublang_dict[language]
            for sublang in sublangs:
                    cls._save_tvl_for_sl(tv, sublang)
        else:
            cls._save_tvl_for_l(tv, language)

    @classmethod
    def update(cls, tv):
        cls.objects.filter(team_video=tv).delete()

        sublang_dict = tv.video.subtitle_language_dict()
        for lang in settings.ALL_LANGUAGES:
            cls._update_for_language(tv, lang[0], sublang_dict)

    @classmethod
    def update_for_language(cls, tv, language):
        cls.objects.filter(team_video=tv, language=language).delete()
        cls._update_for_language(
            tv, language, tv.video.subtitle_language_dict())

class TeamVideoLanguagePair(models.Model):
    team_video = models.ForeignKey(TeamVideo)
    team = models.ForeignKey(Team)
    video = models.ForeignKey(Video)
    # language_0 and subtitle_language_0 are the potential standards.
    language_0 = models.CharField(max_length=16, choices=ALL_LANGUAGES, db_index=True)
    subtitle_language_0 = models.ForeignKey(
        SubtitleLanguage, null=False, related_name="team_video_language_pairs_0")
    language_1 = models.CharField(max_length=16, choices=ALL_LANGUAGES, db_index=True)
    subtitle_language_1 = models.ForeignKey(
        SubtitleLanguage, null=True, related_name="team_video_language_pairs_1")
    language_pair = models.CharField(db_index=True, max_length=16)
    percent_complete = models.IntegerField(db_index=True, default=0)

class TeamMemderManager(models.Manager):
    use_for_related_fields = True
    
    def managers(self):
        return self.get_query_set().filter(is_manager=True)
    
class TeamMember(models.Model):
    team = models.ForeignKey(Team, related_name='members')
    user = models.ForeignKey(User)
    is_manager = models.BooleanField(default=False)
    changes_notification = models.BooleanField(default=True)
    
    objects = TeamMemderManager()
    
    class Meta:
        unique_together = (('team', 'user'),)
    
class Application(models.Model):
    team = models.ForeignKey(Team, related_name='applications')
    user = models.ForeignKey(User, related_name='team_applications')
    note = models.TextField(blank=True)
    
    class Meta:
        unique_together = (('team', 'user'),)
    
    def approve(self):
        TeamMember.objects.get_or_create(team=self.team, user=self.user)
        self.delete()
    
    def deny(self):
        self.delete()
        
class Invite(models.Model):
    team = models.ForeignKey(Team, related_name='invitations')
    user = models.ForeignKey(User, related_name='team_invitations')
    note = models.TextField(blank=True, max_length=200)

    class Meta:
        unique_together = (('team', 'user'),)
    
    def accept(self):
        TeamMember.objects.get_or_create(team=self.team, user=self.user)
        self.delete()
        
    def deny(self):
        self.delete()
    
    def render_message(self):
        return render_to_string('teams/_invite_message.html', {'invite': self})

models.signals.pre_delete.connect(Message.on_delete, Invite)
    
def invite_send_message(sender, instance, created, **kwargs):
    if created:
        msg = Message()
        msg.user = instance.user
        msg.object = instance
        msg.save()
    
post_save.connect(invite_send_message, Invite)
