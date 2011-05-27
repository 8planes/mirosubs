import datetime
from haystack.indexes import *
from haystack import site
from teams import models
from django.conf import settings

class TeamVideoLanguagesIndex(SearchIndex):
    text = CharField(
        document=True, use_template=True, 
        template_name="teams/teamvideo_languages_for_search.txt")
    team_id = IntegerField()
    team_video_pk = IntegerField()
    video_pk = IntegerField()
    video_id = CharField()
    video_title = CharField()
    video_url = CharField()
    original_language = CharField()
    original_language_display = CharField()
    has_lingua_franca = BooleanField()
    absolute_url = CharField()
    video_absolute_url = CharField()
    thumbnail = CharField()
    title = CharField()
    description = CharField()

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
        

        return self.prepared_data

site.register(models.TeamVideo, TeamVideoLanguagesIndex)
