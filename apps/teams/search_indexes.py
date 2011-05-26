import datetime
from haystack.indexes import *
from haystack import site
from teams import models

class TeamVideoLanguagesIndex(SearchIndex):
    text = CharField(
        document=True, use_template=True, 
        template_name="teams/teamvideo_languages_for_search.txt")
    team_id = IntegerField()
    video_title = CharField()

    def prepare(self, obj):
        self.prepared_data = super(TeamVideoLanguagesIndex, self).prepare(obj)
        self.prepared_data['team_id'] = obj.team.id
        self.prepared_data['video_title'] = obj.video.title
        return self.prepared_data

site.register(models.TeamVideo, TeamVideoLanguagesIndex)
