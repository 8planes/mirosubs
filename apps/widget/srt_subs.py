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

"""
Functionality for generating srt files.
"""

import StringIO

def captions_and_translations_to_srt(captions_and_translations):
    # TODO: note this loads the entire string into memory, which will not 
    # scale beautifully. In future, possibly stream directly to response.
    output = StringIO.StringIO()
    for i in range(len(captions_and_translations)):
        translation_to_srt(captions_and_translations[i][1],
                           captions_and_translations[i][0],
                           i, output)
    srt = output.getvalue()
    output.close()
    return srt

def captions_to_srt(subtitles):
    # TODO: note this loads the entire string into memory, which will not 
    # scale beautifully. In future, possibly stream directly to response.
    output = StringIO.StringIO()
    for i in range(len(subtitles)):
        subtitle_to_srt(subtitles[i], i, output)
    srt = output.getvalue()
    output.close()
    return srt

def translation_to_srt(translation, video_caption, index, output):
    subtitle_to_srt_impl(video_caption.caption_text if translation is None \
                         else translation.translation_text, 
                         video_caption, index, output)

def subtitle_to_srt(video_caption, index, output):
    subtitle_to_srt_impl(video_caption.caption_text,
                         video_caption, index, output)

def subtitle_to_srt_impl(text, video_caption, index, output):
    output.write(str(index + 1))
    output.write("\n")
    write_srt_time_line(video_caption, output)
    output.write(text)
    output.write("\n\n")

def write_srt_time_line(video_caption, output):
    write_srt_time(video_caption.start_time, output)
    output.write(" --> ")
    write_srt_time(video_caption.end_time, output)
    output.write("\n")

def write_srt_time(seconds, output):
    seconds_int = int(seconds)
    write_padded_num((seconds_int / 3600) % 60, 2, output)
    output.write(":")
    write_padded_num((seconds_int / 60) % 60, 2, output)
    output.write(":")
    write_padded_num(seconds_int % 60, 2, output)
    output.write(",")
    write_padded_num(int(seconds * 1000) % 1000, 3, output)

def write_padded_num(num, numchars, output):
    strnum = str(num)
    numzeros = numchars - len(strnum)
    for i in range(numzeros):
        output.write("0")
    output.write(strnum)

from math import floor
import codecs

class BaseSubtitles(object):
    file_type = ''
    
    def __init__(self, subtitles, video):
        """
        Use video for extra data in subtitles like Title
        Subtitles is list of {'text': 'text', 'start': 'seconds', 'end': 'seconds'}
        """
        self.subtitles = subtitles
        self.video = video
    
    def __unicode__(self):
        raise Exception('Should return subtitles')
    
class SSASubtitles(BaseSubtitles):
    file_type = 'ssa'
    
    def __unicode__(self):
        #add BOM to fix python default behaviour, because players don't play without it
        return u''.join([unicode(codecs.BOM_UTF8, "utf8"), self._start(), self._content(), self._end()])
    
    def _start(self):
        return u'[Script Info]\r\nTitle: %s\r\n' % self.video.__unicode__()
    
    def _end(self):
        return u''
    
    def format_time(self, time):
        hours = int(floor(time / 3600))
        minutes = int(floor(time % 3600 / 60))
        seconds = int(time % 60)
        fr_seconds = int(time % 1 * 100)
        return u'%i:%02i:%02i.%02i' % (hours, minutes, seconds, fr_seconds)
        
    def _content(self):
        output = []
        output.append(u'[Events]\r\n')
        output.append(u'Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\r\n')
        tpl = u'Dialogue: 0,%s,%s,Default,,0000,0000,0000,,%s\r\n'
        for item in self.subtitles:
            start = self.format_time(item['start'])
            end = self.format_time(item['end'])
            output.append(tpl % (start, end, item['text']))
        return ''.join(output)

from lxml import etree
    
class TTMLSubtitles(BaseSubtitles):
    file_type = 'xml'
    
    def __unicode__(self):
        return u'<?xml version="1.0" encoding="UTF-8"?>\n'\
            +etree.tounicode(self.xml_node(), pretty_print=True)
    
    def xml_node(self):
        tt = etree.Element('tt', nsmap={None: 'http://www.w3.org/2006/04/ttaf1', 'tts': 'http://www.w3.org/2006/04/ttaf1#styling'})
        etree.SubElement(tt, 'head')
        body = etree.SubElement(tt, 'body')
        div = etree.SubElement(body, 'div')
        for item in self.subtitles:
            if not item['text']:
                continue
            attrib = {}
            attrib['begin'] = self.format_time(item['start'])
            attrib['dur'] = self.format_time(item['end']-item['start'])
            p = etree.SubElement(div, 'p', attrib=attrib)
            p.text = item['text']
        return tt
    
    def format_time(self, time):
        hours = int(floor(time / 3600))
        minutes = int(floor(time % 3600 / 60))
        seconds = int(time % 60)
        fr_seconds = int(time % 1 * 100)
        return u'%02i:%02i:%02i.%02i' % (hours, minutes, seconds, fr_seconds)    