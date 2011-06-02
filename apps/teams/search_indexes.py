import datetime
from haystack.indexes import *
from haystack import site
from teams import models
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
    video_title = CharField(indexed=False)
    video_url = CharField(indexed=False)
    original_language = CharField()
    original_language_display = CharField(indexed=False)
    has_lingua_franca = BooleanField()
    absolute_url = CharField(indexed=False)
    video_absolute_url = CharField(indexed=False)
    thumbnail = CharField(indexed=False)
    title = CharField(indexed=False)
    description = CharField(indexed=False)
    is_complete = BooleanField()
    video_complete_date = DateTimeField(null=True)
    # list of completed language codes
    video_completed_langs = MultiValueField(indexed=False)
    # list of completed language absolute urls. should have 1-1 mapping to video_compelted_langs
    video_completed_lang_urls = MultiValueField(indexed=False)

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

        return self.prepared_data

site.register(models.TeamVideo, TeamVideoLanguagesIndex)
