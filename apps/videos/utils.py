from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.conf import settings
from django.utils import simplejson as json
import re

def get_pager(objects, on_page=15, page='1', orphans=0):
    from django.core.paginator import Paginator, InvalidPage, EmptyPage
    
    paginator = Paginator(objects, on_page, orphans=orphans)
    try:
        page = paginator.page(int(page))
    except (EmptyPage, InvalidPage):
        page = paginator.page(paginator.num_pages)
    return page

def send_templated_email(to, subject, body_template, body_dict, 
                         from_email=None, ct="html", fail_silently=False):
    if not isinstance(to, list): to = [to]
    if not from_email: from_email = settings.DEFAULT_FROM_EMAIL

    message = render_to_string(body_template, body_dict)

    email = EmailMessage(subject, message, from_email, to)
    email.content_subtype = ct
    email.send(fail_silently)

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

class YoutubeSubtitleParser(SubtitleParser):
    
    def __init__(self, data):
        data = json.loads(data)
        if data:
            data = data[0]
            self.subtitles = data['plaintext_list']
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
        output['start_time'] = item['start_ms'] / 1000
        output['end_time'] = output['start_time'] + item['dur_ms'] / 1000
        output['subtitle_text'] = item['text']
        return output
 
from xml.dom.minidom import parseString
from xml.parsers.expat import ExpatError
from django.utils.html import strip_tags

class TtmlSubtitleParser(SubtitleParser):
    
    def __init__(self, subtitles):
        try:
            dom = parseString(subtitles)
        except ExpatError:
            raise SubtitleParserError('Incorrect format of TTML subtitles')
        self.nodes = dom.getElementsByTagName('body')[0].getElementsByTagName('p')
        
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
            
            d_hour, d_min, d_sec = dur.split(':')
            end = start + int(d_hour)*60*60 + int(d_min)*60 + float(d_sec)
        except ValueError:
            return -1
        
        return start, end
        
    def _get_data(self, node):
        output = {
            'subtitle_text': strip_tags(node.toxml())
        }        
        output['start_time'], output['end_time'] = \
            self._get_time(node.getAttribute('begin'), node.getAttribute('dur'))
        return output
        
    def _result_iter(self):
        for item in self.nodes:
            yield self._get_data(item)
        
class SrtSubtitleParser(SubtitleParser):
    
    def __init__(self, subtitles):
        self._clean_pattern = re.compile(r'\{.*?\}', re.DOTALL)
        pattern = r'\d+\n'
        pattern += r'(?P<s_hour>\d{2}):(?P<s_min>\d{2}):(?P<s_sec>\d{2}),(?P<s_secfr>\d+)'
        pattern += r' --> '
        pattern += r'(?P<e_hour>\d{2}):(?P<e_min>\d{2}):(?P<e_sec>\d{2}),(?P<e_secfr>\d+)'
        pattern += r'\n(?P<text>.+?)\n\n'
        subtitles = strip_tags(subtitles)
        super(SrtSubtitleParser, self).__init__(subtitles, pattern, [re.DOTALL])
        #replace \r\n to \n and fix end of last subtitle
        self.subtitles = self.subtitles.replace('\r\n', '\n')+'\n\n'
    
    def _get_time(self, hour, min, sec, secfr):
        return int(hour)*60*60+int(min)*60+int(sec)+float('.'+secfr)
    
    def _get_data(self, match):
        r = match.groupdict()
        output = {}
        output['start_time'] = self._get_time(r['s_hour'], r['s_min'], r['s_sec'], r['s_secfr'])
        output['end_time'] = self._get_time(r['e_hour'], r['e_min'], r['e_sec'], r['e_secfr'])
        output['subtitle_text'] = self._clean_pattern.sub('', r['text'])
        return output
    
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
        self.subtitles = self.subtitles.replace('\r\n', '\n')+'\n'
