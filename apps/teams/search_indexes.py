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
    video_title = CharField()
    original_language = CharField()
    has_lingua_franca = BooleanField()

    def prepare(self, obj):
        self.prepared_data = super(TeamVideoLanguagesIndex, self).prepare(obj)
        self.prepared_data['team_id'] = obj.team.id
        self.prepared_data['video_title'] = obj.video.title
        original_sl = obj.video.subtitle_language()
        self.prepared_data['original_language'] = '' if not original_sl \
            else original_sl.language
        self.prepared_data['has_lingua_franca'] = \
            bool(set(settings.LINGUA_FRANCAS) &
                 set([sl.language for sl in 
                      obj.video.subtitlelanguage_set.all() if 
                      sl.is_dependable()]))
        return self.prepared_data

site.register(models.TeamVideo, TeamVideoLanguagesIndex)
