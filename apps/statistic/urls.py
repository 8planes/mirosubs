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
from django.conf.urls.defaults import *
from statistic.models import TweeterShareStatistic as TwSt, FBShareStatistic as FbSt

urlpatterns = patterns('statistic.views',
    url('^$', 'index', name='index'),
    url('^users_statistic/$', 'users_statistic', name='users_statistic'),
    url('^videos_statistic/$', 'videos_statistic', name='videos_statistic'),
    url('^languages_statistic/$', 'languages_statistic', name='languages_statistic'),
    url('^language_statistic/(?P<lang>[\-\w]+)/$', 'language_statistic', name='language_statistic'),
    url('^fb_st/$', 'update_share_statistic', {'cls': FbSt}, 'fb_update_share_statistic'),
    url('^tweeter_st/$', 'update_share_statistic', {'cls': TwSt}, 'tw_update_share_statistic'),
)