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

from django.contrib import admin
from videos.models import Video, SubtitleLanguage, SubtitleVersion, Subtitle

class VideoAdmin(admin.ModelAdmin):
    list_display = ['__unicode__', 'title']
    search_fields = ['video_id', 'title', 'videourl__url']

class SubtitleLanguageAdmin(admin.ModelAdmin):
    list_display = ['video', 'is_original', 'language', 'is_complete', 'was_complete']
    list_filter = ['is_original', 'is_complete']

class SubtitleVersionAdmin(admin.ModelAdmin):
    list_display = ['language', 'version_no', 'note', 'time_change', 'text_change']
    list_filter = []

class SubtitleAdmin(admin.ModelAdmin):
    list_display = ['version', 'subtitle_id', 'subtitle_order', 'subtitle_text', 'start_time', 'end_time']

admin.site.register(Subtitle, SubtitleAdmin)
admin.site.register(SubtitleVersion, SubtitleVersionAdmin)    
admin.site.register(Video, VideoAdmin)
admin.site.register(SubtitleLanguage, SubtitleLanguageAdmin)
