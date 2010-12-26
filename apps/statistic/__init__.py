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
from datetime import datetime
from utils.redis_utils import default_connection, RedisKey

SUBTITLES_FETCH_PREFIX = 'StSubFetch'

video_view_counter = RedisKey('StVideoView')
sub_fetch_total_counter = RedisKey('StSubFetchTotal')
widget_views_total_counter = RedisKey('StWidgetViewsTotal')

def get_fetch_subtitles_key(video, lang=None, date=None):
    if not date:
        date = datetime.today()
    
    key = '%s:%s' % (SUBTITLES_FETCH_PREFIX, video.video_id)
    
    if lang:
        key += ':%s' % lang
    
    key += ':%s:%s:%s' % (date.day, date.month, date.year)
    return key
    
def update_subtitles_fetch_counter(video, sub_lang=None, date=None):
    if sub_lang:
        lang = sub_lang.language
    else:
        lang = None
    key = get_fetch_subtitles_key(video, lang, date)
    RedisKey(key).incr()
    sub_fetch_total_counter.incr()