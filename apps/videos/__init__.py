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

from utils.subtitles import MAX_SUB_TIME

UNSYNCED_MARKER = -1

def is_synced_value(v):
    return v != -1 and v != None and v < MAX_SUB_TIME

def is_synced(obj):
    if obj.start_time is None or  obj.end_time is None:
        return False
    return is_synced_value( obj.start_time) and is_synced_value(obj.start_time)
    
def format_time(time):
    if not is_synced_value(time):
         return ""
    t = int(round(time))
    s = t % 60
    s = s > 9 and s or '0%s' % s
    return '%s:%s' % (t / 60, s)   


class EffectiveSubtitle:
    def __init__(self, subtitle_id, text, start_time, end_time, sub_order, pk):
        self.subtitle_id = subtitle_id
        self.text = text
        if start_time is None:
            start_time = UNSYNCED_MARKER
        self.start_time = start_time    
        if end_time is None:
            end_time = UNSYNCED_MARKER
            
        self.end_time = end_time 
        self.sub_order = sub_order
        self.pk = pk
    
    def for_json(self):
        return {
            'subtitle_id': self.subtitle_id,
            'text': self.text,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'sub_order': self.sub_order 
        }

    def has_complete_timing(self):
        return is_synced(self)
    
    def for_generator(self):
        return {
            'text': self.text,
            'start': self.start_time,
            'end': self.end_time,
            'id': self.pk
        }

    def has_same_timing(self, subtitle):
        return self.start_time == subtitle.start_time and \
            self.end_time == subtitle.end_time
    
    @classmethod
    def for_subtitle(cls, subtitle):
        return EffectiveSubtitle(
            subtitle.subtitle_id,
            subtitle.subtitle_text,
            subtitle.start_time,
            subtitle.end_time,
            subtitle.subtitle_order,
            subtitle.pk)

    @classmethod
    def for_dependent_translation(cls, subtitle, translation):
        return EffectiveSubtitle(
            subtitle.subtitle_id,
            translation.subtitle_text,
            subtitle.start_time,
            subtitle.end_time,
            subtitle.subtitle_order,
            subtitle.pk)

    def duplicate_for(self, draft):
        from videos.models import Subtitle
        return Subtitle(
            draft=draft,
            subtitle_id=self.subtitle_id,
            subtitle_order=self.sub_order,
            subtitle_text=self.text,
            start_time=self.start_time,
            end_time=self.end_time)

    def display_time(self):
        t = self.start_time
        return '' if t < 0 else format_time(t)

    def display_end_time(self):
        t = self.end_time
        return '' if t < 0 else format_time(t)
