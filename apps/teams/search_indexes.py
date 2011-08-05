import json
import datetime
from haystack.indexes import *
from haystack import site
from teams import models
from apps.teams.moderation import WAITING_MODERATION
from apps.videos.models import SubtitleLanguage
from django.conf import settings
from django.utils.translation import ugettext as _

LANGUAGES_DICT = dict(settings.ALL_LANGUAGES)


class TeamVideoLanguagesIndex(SearchIndex):
    text = CharField(
        document=True, use_template=True, 
        template_name="teams/teamvideo_languages_for_search.txt")
    team_id = IntegerField()
    team_video_pk = IntegerField(indexed=False)
    video_pk = IntegerField(indexed=False)
    video_id = CharField(indexed=False)
    video_title = CharField(indexed=True)
    video_url = CharField(indexed=False)
    original_language = CharField()
    original_language_display = CharField(indexed=False)
    has_lingua_franca = BooleanField()
    absolute_url = CharField(indexed=False)
    video_absolute_url = CharField(indexed=False)
    thumbnail = CharField(indexed=False)
    title = CharField(indexed=True)
    description = CharField(indexed=False)
    is_complete = BooleanField()
    video_complete_date = DateTimeField(null=True)
    # list of completed language codes
    video_completed_langs = MultiValueField(indexed=False)
    # list of completed language absolute urls. should have 1-1 mapping to video_compelted_langs
    video_completed_lang_urls = MultiValueField(indexed=False)

    needs_moderation = BooleanField()
    latest_submission_date = DateTimeField(null=True)
    
    moderation_languages_names = MultiValueField(null=True)
    moderation_languages_pks = MultiValueField(null=True)
    # we'll serialize data from versions here -> links and usernames
    # that will be on the appgove all for that language
    moderation_version_info = CharField(indexed=False)
    
    def prepare(self, obj):
        self.prepared_data = super(TeamVideoLanguagesIndex, self).prepare(obj)
        self.prepared_data['team_id'] = obj.team.id
        self.prepared_data['team_video_pk'] = obj.id
        self.prepared_data['video_pk'] = obj.video.id
        self.prepared_data['video_id'] = obj.video.video_id
        self.prepared_data['video_title'] = obj.video.title
        self.prepared_data['video_url'] = obj.video.get_video_url()
        original_sl = obj.video.subtitle_language()
        if original_sl:
            self.prepared_data['original_language_display'] = \
                original_sl.get_language_display()
            self.prepared_data['original_language'] = original_sl.language
        else:
            self.prepared_data['original_language_display'] = ''
            self.prepared_data['original_language'] = ''
        self.prepared_data['has_lingua_franca'] = \
            bool(set(settings.LINGUA_FRANCAS) &
                 set([sl.language for sl in 
                      obj.video.subtitlelanguage_set.all() if 
                      sl.is_dependable()]))
        self.prepared_data['absolute_url'] = obj.get_absolute_url()
        self.prepared_data['video_absolute_url'] = obj.video.get_absolute_url()
        self.prepared_data['thumbnail'] = obj.get_thumbnail()
        self.prepared_data['title'] = unicode(obj)
        self.prepared_data['description'] = obj.description
        self.prepared_data['is_complete'] = obj.video.complete_date is not None
        self.prepared_data['video_complete_date'] = obj.video.complete_date
        
        completed_sls = obj.video.completed_subtitle_languages()
        self.prepared_data['video_completed_langs'] = \
            [sl.language for sl in completed_sls]
        self.prepared_data['video_completed_lang_urls'] = \
            [sl.get_absolute_url() for sl in completed_sls]

        
        self.prepares_moderation_info( obj, self.prepared_data)
        return self.prepared_data

    def prepares_moderation_info(self, obj, prepared_data):
        mod_on_same_team =  obj.video.moderated_by == obj.team
        on_mod = obj.team.get_pending_moderation().filter(language__video=obj.video).count() > 0
        self.prepared_data["needs_moderation"] =  mod_on_same_team and on_mod

        self.moderation_languages_urls = []
        self.moderation_languages_names = []
        self.moderation_version_info = ""
        
        pending_versions = obj.team.get_pending_moderation()
        pending_languages = list(SubtitleLanguage.objects.filter(video=obj.video,
                                                            subtitleversion__moderation_status=WAITING_MODERATION).distinct("language"))
        if len(pending_languages) == 0 or self.prepared_data["needs_moderation"] is False:
            return

        prepared_data['moderation_languages_names'] =  []
        prepared_data['moderation_languages_pks'] =  []
        moderation_version_info = []
        for lang in pending_languages:
            prepared_data['moderation_languages_names'].append(lang.language)
            prepared_data['moderation_languages_pks'].append(lang.pk)
            versions = pending_versions.filter(language=lang)
            version_info = []
            for version in versions:
                version_info.append({
                        "username":version.user.username,
                        "user_id":version.user.pk,
                        "pk":version.pk
                })
            moderation_version_info.append( version_info)
        self.prepared_data["latest_submission_date"] = pending_versions.order_by("-datetime_started")[0].datetime_started
        self.prepared_data['moderation_version_info'] = json.dumps(moderation_version_info)


                
            
site.register(models.TeamVideo, TeamVideoLanguagesIndex)
