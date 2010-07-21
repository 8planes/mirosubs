from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.conf import settings
import re

def get_pager(objects, on_page=15, page='1', orphans=0):
    from django.core.paginator import Paginator, InvalidPage, EmptyPage
    
    paginator = Paginator(objects, on_page, orphans=orphans)
    try:
        page = paginator.page(int(page))
    except (EmptyPage, InvalidPage):
        page = paginator.page(paginator.num_pages)
    return page

def send_templated_email(to, subject, body_template, body_dict, from_email=None, ct="html", fail_silently=False):
    if not isinstance(to, list): to = [to]
    if not from_email: from_email = settings.DEFAULT_FROM_EMAIL

    message = render_to_string(body_template, body_dict)

    email = EmailMessage(subject, message, from_email, to)
    email.content_subtype = ct
    email.send(fail_silently)
    
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
        for item in self.matches:
            yield self._get_data(item)

    def _get_data(self, match):
        return match.groupdict()
    
    def _get_matches(self):
        return self._pattern.finditer(self.subtitles)
    matches = property(_get_matches)
        
class SrtSubtitleParser(SubtitleParser):
    
    def __init__(self, file):
        pattern = r'\d+\n'
        pattern += r'(?P<s_hour>\d{2}):(?P<s_min>\d{2}):(?P<s_sec>\d{2}),(?P<s_secfr>\d+)'
        pattern += r' --> '
        pattern += r'(?P<e_hour>\d{2}):(?P<e_min>\d{2}):(?P<e_sec>\d{2}),(?P<e_secfr>\d+)'
        pattern += r'\r?\n(?P<text>.+?)\n\n'        
        super(SrtSubtitleParser, self).__init__(file, pattern, [re.DOTALL])
        #replace \r\n to \n and fix end of last subtitle
        self.subtitles = self.subtitles.replace('\r\n', '\n')+'\n\n'
    
    def _get_time(self, hour, min, sec, secfr):
        return int(hour)*60*60+int(min)*60+int(sec)+float('.'+secfr)
    
    def _get_data(self, match):
        r = match.groupdict()
        output = {}
        output['start_time'] = self._get_time(r['s_hour'], r['s_min'], r['s_sec'], r['s_secfr'])
        output['end_time'] = self._get_time(r['e_hour'], r['e_min'], r['e_sec'], r['e_secfr'])
        output['caption_text'] = r['text']
        return output
    
class AssSubtitleParser(SrtSubtitleParser):
    def __init__(self, file):
        pattern = r'Dialogue: [\w=]+,' #Dialogue: <Marked> or <Layer>,
        pattern += '(?P<s_hour>\d):(?P<s_min>\d{2}):(?P<s_sec>\d{2})[\.\:](?P<s_secfr>\d+),' #<Start>,
        pattern += r'(?P<e_hour>\d):(?P<e_min>\d{2}):(?P<e_sec>\d{2})[\.\:](?P<e_secfr>\d+),' #<End>,
        pattern += r'[\w ]+,' #<Style>,
        pattern += '[\w ]*,' #<Character name>,
        pattern += '\d{4},\d{4},\d{4},' #<MarginL>,<MarginR>,<MarginV>,
        pattern += '[\w ]*,' #<Efect>,
        pattern += '(?:\{.*?\})?(?P<text>.+?)\n' #[{<Override control codes>}]<Text> 
        super(SrtSubtitleParser, self).__init__(file, pattern, [re.DOTALL])
        #replace \r\n to \n and fix end of last subtitle
        self.subtitles = self.subtitles.replace('\r\n', '\n')+'\n'