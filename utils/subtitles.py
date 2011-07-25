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

#  Based on: http://www.djangosnippets.org/snippets/73/
#
#  Modified by Sean Reifschneider to be smarter about surrounding page
#  link context.  For usage documentation see:
#
#     http://www.tummy.com/Community/Articles/django-pagination/
from django.utils import simplejson as json
from django.db.models import ObjectDoesNotExist
from datetime import datetime
import re
import random
from uuid import uuid4
from lxml import etree
from utils.clean_xml import htmlentitydecode

# see video.models.Subtitle..start_time
MAX_SUB_TIME = (60 * 60 * 99) -1 

def is_version_same(version, parser):
    if not version:
        return False
    
    subtitles = list(parser)
    
    if version.subtitle_set.count() != len(subtitles):
        return False
    
    for item in zip(subtitles, version.subtitle_set.all()):
        if item[0]['subtitle_text'] != item[1].subtitle_text or \
            item[0]['start_time'] != item[1].start_time or \
            item[0]['end_time'] != item[1].end_time:
                return False
            
    return True

def save_subtitle(video, language, parser, user=None, update_video=True):
    from videos.models import SubtitleVersion, Subtitle
    from videos.tasks import video_changed_tasks

    key = str(uuid4()).replace('-', '')

    video._make_writelock(user, key)
    video.save()
    
    try:
        old_version = language.subtitleversion_set.all()[:1].get()    
        version_no = old_version.version_no + 1
    except ObjectDoesNotExist:
        old_version = None
        version_no = 0
    version = None
    if not is_version_same(old_version, parser):
        version = SubtitleVersion(
            language=language, version_no=version_no,
            datetime_started=datetime.now(), user=user,
            note=u'Uploaded', is_forked=True, time_change=1, text_change=1)
        version.save()

        ids = []

        for i, item in enumerate(parser):
            id = int(random.random()*10e12)
            while id in ids:
                id = int(random.random()*10e12)
            ids.append(id)
            caption = Subtitle(**item)
            caption.version = version
            caption.subtitle_id = str(id)
            caption.subtitle_order = i+1
            caption.save()
            
    language.video.release_writelock()
    language.video.save()
    translations = video.subtitlelanguage_set.filter(standard_language=language)
    [t.fork(from_version=old_version, user=user) for t in translations]
    if update_video:
        video_changed_tasks.delay(video.id, None if version is None else version.id)
        
    return language  
            
class SubtitleParserError(Exception):
    pass
    
class SubtitleParser(object):
    
    def __init__(self, subtitles, pattern, flags=[]):
        self.subtitles = subtitles
        self.pattern = pattern
        self._pattern = re.compile(pattern, *flags)
        
    def __iter__(self):
        return self._result_iter()
    
    def __len__(self):
        return len(self._pattern.findall(self.subtitles))
    
    def __nonzero__(self):
        return bool(self._pattern.search(self.subtitles))
     
    def _result_iter(self):
        for item in self._matches:
            yield self._get_data(item)

    def _get_data(self, match):
        return match.groupdict()
    
    def _get_matches(self):
        return self._pattern.finditer(self.subtitles)
    _matches = property(_get_matches)

class TxtSubtitleParser(SubtitleParser):
    _linebreak_re = re.compile(r"\n\n|\r\n\r\n|\r\r")

    def __init__(self, subtitles, linebreak_re=_linebreak_re):
        self.subtitles = linebreak_re.split(subtitles)
        
    def __len__(self):
        return len(self.subtitles)
    
    def __nonzero__(self):
        return bool(self.subtitles)      
    
    def _result_iter(self):
        for item in self.subtitles:
            output = {}
            output['start_time'] = -1
            output['end_time'] = -1
            output['subtitle_text'] = item      
            yield output  

class YoutubeXMLParser(SubtitleParser):
    
    def __init__(self, xml):
        if not isinstance(xml, etree._Element):
            xml = etree.fromstring(xml)
        
        self.xml = xml
        self.subtitles = xml.xpath('text')

    def __len__(self):
        return len(self.subtitles)
    
    def __nonzero__(self):
        return bool(self.subtitles)
    
    def _result_iter(self):
        for item in self.subtitles:
            yield self._get_data(item)

    def _get_data(self, item):
        output = {}
        output['start_time'] = float(item.get('start'))
        output['end_time'] = output['start_time'] + float(item.get('dur'))
        output['subtitle_text'] = htmlentitydecode(item.text)
        return output
        
class YoutubeSubtitleParser(SubtitleParser):
    
    def __init__(self, data):
        try:
            data = json.loads(data)
        except json.JSONDecodeError:
            data = None
        if data:
            data = data[0]
            self.subtitles = data['plaintext_list']
            self.subtitles.sort(key=lambda i: i['start_ms'])
            self.language = data['language']
        else:
            self.subtitles = []
            self.language = None            
    
    def __len__(self):
        return len(self.subtitles)
    
    def __nonzero__(self):
        return bool(self.subtitles)
    
    def _result_iter(self):
        for item in self.subtitles:
            yield self._get_data(item)

    def _get_data(self, item):
        output = {}
        output['start_time'] = item['start_ms'] / 1000.
        output['end_time'] = (item['start_ms'] + item['dur_ms']) / 1000.
        output['subtitle_text'] = item['text']
        return output
 
from xml.dom.minidom import parseString
from xml.parsers.expat import ExpatError
from django.utils.html import strip_tags
from utils.clean_xml import htmlentitydecode

class STSubtitleParser(SubtitleParser):

    def __init__(self, subtitles):
        try:
            dom = parseString(subtitles.encode('utf8'))
            self.nodes = dom.getElementsByTagName('transcript')[0].getElementsByTagName('content')
        except (ExpatError, IndexError):
            raise SubtitleParserError('Incorrect format of SpeakerText subtitles')

    def __len__(self):
        return len(self.nodes)
    
    def __nonzero__(self):
        return bool(len(self.nodes))
    
    def _get_time(self, val):
        try:
            return int(val) / 1000.
        except ValueError:
            return -1
    
    def _get_data(self, node):

        output = {
            'subtitle_text': htmlentitydecode(strip_tags(node.toxml()).strip())
        }
        output['start_time'] = self._get_time(node.getAttribute('timestamp'))
        output['end_time'] = self._get_time(node.getAttribute('end_timestamp'))

        return output
        
    def _result_iter(self):
        for item in self.nodes:
            yield self._get_data(item)
            
class TtmlSubtitleParser(SubtitleParser):
    
    def __init__(self, subtitles):
        try:
            dom = parseString(subtitles.encode('utf8'))
            self.nodes = dom.getElementsByTagName('body')[0].getElementsByTagName('p')
        except (ExpatError, IndexError):
            raise SubtitleParserError('Incorrect format of TTML subtitles')
        
    def __len__(self):
        return len(self.nodes)
    
    def __nonzero__(self):
        return bool(len(self.nodes))
    
    def _get_time(self, begin, dur):
        if not begin or not dur:
            return -1
        
        try:
            hour, min, sec = begin.split(':')
            
            start = int(hour)*60*60 + int(min)*60 + float(sec)
            if start > MAX_SUB_TIME:
                return -1
            
            d_hour, d_min, d_sec = dur.split(':')
            end = start + int(d_hour)*60*60 + int(d_min)*60 + float(d_sec)
        except ValueError:
            return -1
        
        return start, end
        
    def _get_data(self, node):
        output = {
            'subtitle_text': htmlentitydecode(strip_tags(node.toxml()))
        }        
        output['start_time'], output['end_time'] = \
            self._get_time(node.getAttribute('begin'), node.getAttribute('dur'))
        return output
        
    def _result_iter(self):
        for item in self.nodes:
            yield self._get_data(item)
        
class SrtSubtitleParser(SubtitleParser):
    _clean_pattern = re.compile(r'\{.*?\}', re.DOTALL)
    
    def __init__(self, subtitles):
        pattern = r'\d+\n'
        pattern += r'(?P<s_hour>\d{2}):(?P<s_min>\d{2}):(?P<s_sec>\d{2})(,(?P<s_secfr>\d*))?'
        pattern += r' --> '
        pattern += r'(?P<e_hour>\d{2}):(?P<e_min>\d{2}):(?P<e_sec>\d{2})(,(?P<e_secfr>\d*))?'
        pattern += r'\n(\n|(?P<text>.+?)\n\n)'
        subtitles = strip_tags(subtitles)
        super(SrtSubtitleParser, self).__init__(subtitles, pattern, [re.DOTALL])
        #replace \r\n to \n and fix end of last subtitle
        self.subtitles = self.subtitles.replace('\r\n', '\n')+u'\n\n'
    
    def _get_time(self, hour, min, sec, secfr):
        if secfr is None:
            secfr = '0'
        return int(hour)*60*60+int(min)*60+int(sec)+float('.'+secfr)
    
    def _get_data(self, match):
        r = match.groupdict()
        output = {}
        output['start_time'] = self._get_time(r['s_hour'], r['s_min'], r['s_sec'], r['s_secfr'])
        output['end_time'] = self._get_time(r['e_hour'], r['e_min'], r['e_sec'], r['e_secfr'])
        output['subtitle_text'] = '' if r['text'] is None else \
            self._clean_pattern.sub('', r['text'])
        return output

class SbvSubtitleParser(SrtSubtitleParser):

    def __init__(self, subtitles):
        pattern = r'(?P<s_hour>\d{1}):(?P<s_min>\d{2}):(?P<s_sec>\d{2})\.(?P<s_secfr>\d{3})'
        pattern += r','
        pattern += r'(?P<e_hour>\d{1}):(?P<e_min>\d{2}):(?P<e_sec>\d{2})\.(?P<e_secfr>\d{3})'
        pattern += r'\n(?P<text>.+?)\n\n'
        subtitles = strip_tags(subtitles)
        super(SrtSubtitleParser, self).__init__(subtitles, pattern, [re.DOTALL])
        #replace \r\n to \n and fix end of last subtitle
        self.subtitles = self.subtitles.replace('\r\n', '\n')+u'\n\n'
        
class SsaSubtitleParser(SrtSubtitleParser):
    def __init__(self, file):
        pattern = r'Dialogue: [\w=]+,' #Dialogue: <Marked> or <Layer>,
        pattern += r'(?P<s_hour>\d):(?P<s_min>\d{2}):(?P<s_sec>\d{2})[\.\:](?P<s_secfr>\d+),' #<Start>,
        pattern += r'(?P<e_hour>\d):(?P<e_min>\d{2}):(?P<e_sec>\d{2})[\.\:](?P<e_secfr>\d+),' #<End>,
        pattern += r'[\w ]+,' #<Style>,
        pattern += r'[\w ]*,' #<Character name>,
        pattern += r'\d{4},\d{4},\d{4},' #<MarginL>,<MarginR>,<MarginV>,
        pattern += r'[\w ]*,' #<Efect>,
        pattern += r'(?:\{.*?\})?(?P<text>.+?)\n' #[{<Override control codes>}]<Text> 
        super(SrtSubtitleParser, self).__init__(file, pattern, [re.DOTALL])
        #replace \r\n to \n and fix end of last subtitle
        self.subtitles = self.subtitles.replace('\r\n', '\n')+u'\n'
