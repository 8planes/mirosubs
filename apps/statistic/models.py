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
from django.db import models
from auth.models import CustomUser as User

class BaseShareStatistic(models.Model):
    user = models.ForeignKey(User, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
        
    class Meta:
        abstract = True

class EmailShareStatistic(BaseShareStatistic):
    pass
    
class TweeterShareStatistic(BaseShareStatistic):
    pass

class FBShareStatistic(BaseShareStatistic):
    pass

class SubtitleFetchStatistic(models.Model):
    video = models.ForeignKey('videos.Video')
    created = models.DateTimeField(auto_now_add=True)    