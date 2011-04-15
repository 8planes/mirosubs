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

from videos.forms import VideoForm, SubtitlesUploadBaseForm
from utils import SrtSubtitleParser, SsaSubtitleParser, TtmlSubtitleParser, SubtitleParserError, SbvSubtitleParser, TxtSubtitleParser
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import force_unicode
from django import forms
import chardet

class AddSubtitlesForm(SubtitlesUploadBaseForm):
    FORMAT_CHOICES = (
        ('srt', 'srt'),
        ('ass', 'ass'),
        ('ssa', 'ssa'),
        ('ttml', 'ttml'),
        ('sbv', 'sbv')
    )
    subtitles = forms.CharField(max_length=256*1024)
    format = forms.ChoiceField(choices=FORMAT_CHOICES)
    
    def __init__(self, *args, **kwargs):
        super(AddSubtitlesForm, self).__init__(*args, **kwargs)
        self.fields['video'].to_field_name = 'video_id'
    
    @classmethod
    def get_form_instance(cls, request, data):
        return cls(request.user, data)

    def clean(self):
        subtitles = self.cleaned_data.get('subtitles')
        format = self.cleaned_data.get('format')
        
        if subtitles and format:
            try:
                try:
                    subtitles = subtitles.encode('utf8')
                    encoding = chardet.detect(subtitles)['encoding']
                except UnicodeDecodeError,e:
                    encoding = 'utf-8'
                if not encoding:
                    raise forms.ValidationError(_(u'Can not detect file encoding'))
                parser = self._get_parser(format)(force_unicode(subtitles, encoding))
                if not parser:
                    raise forms.ValidationError(_(u'Incorrect subtitles format'))
                self.parser = parser
            except SubtitleParserError, e:
                raise forms.ValidationError(e)

        return self.cleaned_data

    def save(self):
        if hasattr(self, 'parser'):
            return self.save_subtitles(self.parser)

    def _get_parser(self, format):
        if format == 'srt':
            return SrtSubtitleParser
        if format in ['ass', 'ssa']:
            return SsaSubtitleParser
        if format == 'ttml':
            return TtmlSubtitleParser
        if format == 'sbv':
            return SbvSubtitleParser
    
class GetVideoForm(VideoForm):
    
    def __init__(self, *args, **kwargs):
        super(GetVideoForm, self).__init__(*args, **kwargs)
        self.fields['video_url'].required = False

    @classmethod
    def get_form_instance(cls, request, data):
        return cls(request.user, data)
        
    def save(self):
        video_url = self.cleaned_data.get('video_url')
        self.created = False
        
        if not video_url:
            return
        else:
            return super(GetVideoForm, self).save()
