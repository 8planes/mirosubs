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

from django import forms
from videos.models import Video, UserTestResult, SubtitleLanguage, VideoFeed
from django.core.mail import EmailMessage, send_mail
from django.conf import settings
from datetime import datetime
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _
import re
from utils import SrtSubtitleParser, SsaSubtitleParser, TtmlSubtitleParser, SubtitleParserError, SbvSubtitleParser, TxtSubtitleParser
from utils.subtitles import save_subtitle
from django.utils.encoding import force_unicode, DjangoUnicodeDecodeError
import chardet
from math_captcha.forms import MathCaptchaForm
from django.utils.safestring import mark_safe
from django.db.models import ObjectDoesNotExist
from videos.types import video_type_registrar, VideoTypeError
from videos.models import VideoUrl
from utils.forms import AjaxForm, EmailListField, UsernameListField
from gdata.youtube.service import YouTubeService
from videos.tasks import video_changed_tasks
from utils.translation import get_languages_list
from utils.forms import StripRegexField, FeedURLField
from videos.feed_parser import FeedParser, FeedParserError
from utils.forms import ReCaptchaField

ALL_LANGUAGES = [(val, _(name)) for val, name in settings.ALL_LANGUAGES]
KB_SIZELIMIT = 512

class TranscriptionFileForm(forms.Form, AjaxForm):
    txtfile = forms.FileField()
    
    def clean_txtfile(self):
        f = self.cleaned_data['txtfile']
        
        if f.name.split('.')[-1] != 'txt':
            raise forms.ValidationError(_('File should have txt format'))
        
        if f.size > KB_SIZELIMIT * 1024:
            raise forms.ValidationError(_(
                    u'File size should be less {0} kb'.format(KB_SIZELIMIT)))

        text = f.read()
        encoding = chardet.detect(text)['encoding']
        if not encoding:
            raise forms.ValidationError(_(u'Can not detect file encoding'))
        try:
            self.file_text = force_unicode(text, encoding)
        except DjangoUnicodeDecodeError:
            raise forms.ValidationError(_(u'Can\'t encode file. It should have utf8 encoding.'))
        f.seek(0)
                
        return f

    def clean_subtitles(self):
        subtitles = self.cleaned_data['subtitles']
        if subtitles.size > KB_SIZELIMIT * 1024:
            raise forms.ValidationError(_(
                    u'File size should be less {0} kb'.format(KB_SIZELIMIT)))
        parts = subtitles.name.split('.')
        if len(parts) < 1 or not parts[-1].lower() in ['srt', 'ass', 'ssa', 'xml', 'sbv']:
            raise forms.ValidationError(_(u'Incorrect format. Upload .srt, .ssa, .sbv or .xml (TTML  format)'))
        try:
            text = subtitles.read()
            encoding = chardet.detect(text)['encoding']
            if not encoding:
                raise forms.ValidationError(_(u'Can not detect file encoding'))
            if not self._get_parser(subtitles.name)(force_unicode(text, encoding)):
                raise forms.ValidationError(_(u'Incorrect subtitles format'))
        except SubtitleParserError, e:
            raise forms.ValidationError(e)
        subtitles.seek(0)
        return subtitles

class CreateVideoUrlForm(forms.ModelForm):
    
    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(CreateVideoUrlForm, self).__init__(*args, **kwargs)
        self.fields['video'].widget = forms.HiddenInput()
    
    class Meta:
        model = VideoUrl
        fields = ('url', 'video')
        
    def clean_url(self):
        url = self.cleaned_data['url']
        
        try:
            video_type = video_type_registrar.video_type_for_url(url)
        except VideoTypeError, e:
            raise forms.ValidationError(e)
        
        if not video_type:
            raise forms.ValidationError(mark_safe(_(u"""Universal Subtitles does not support that website or video format.
If you'd like to us to add support for a new site or format, or if you
think there's been some mistake, <a
href="mailto:%s">contact us</a>!""") % settings.FEEDBACK_EMAIL)) 
        self._video_type = video_type            
        return video_type.convert_to_video_url()
    
    def clean(self):
        data = super(CreateVideoUrlForm, self).clean()
        video = data.get('video')
        if video and not video.allow_video_urls_edit and not self.user.has_perm('videos.add_videourl'):
            raise forms.ValidationError(_('You have not permission add video URL for this video'))
        
        return self.cleaned_data
        
    def save(self, commit=True):
        obj = super(CreateVideoUrlForm, self).save(False)
        obj.type = self._video_type.abbreviation
        obj.added_by = self.user
        obj.videoid = self._video_type.video_id or ''
        commit and obj.save()
        return obj
    
    def get_errors(self):
        output = {}
        for key, value in self.errors.items():
            output[key] = '/n'.join([force_unicode(i) for i in value])
        return output
    
class SubtitlesUploadBaseForm(forms.Form):
    language = forms.ChoiceField(choices=ALL_LANGUAGES, initial='en')
    video_language = forms.ChoiceField(required=False, choices=ALL_LANGUAGES, initial='en')
    video = forms.ModelChoiceField(Video.objects)

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(SubtitlesUploadBaseForm, self).__init__(*args, **kwargs)
        self.fields['language'].choices = get_languages_list()
        self.fields['video_language'].choices = get_languages_list()
        
    def clean_video(self):
        video = self.cleaned_data['video']
        if video.is_writelocked:
            raise forms.ValidationError(_(u'Somebody is subtitling this video right now. Try later.'))
        return video

    def _save_original_language(self, video, video_language):
        original_language = video.subtitle_language()

        if original_language:
            if original_language.language:
                try:
                    language_exists = video.subtitlelanguage_set.exclude(pk=original_language.pk) \
                        .get(language=video_language)
                    original_language.is_original = False
                    original_language.save()
                    language_exists.is_original = True
                    language_exists.save()
                except ObjectDoesNotExist:
                    original_language.language = video_language
                    original_language.save()
            else:
                try:
                    language_exists = video.subtitlelanguage_set.exclude(pk=original_language.pk) \
                        .get(language=video_language)
                    
                    latest_version = original_language.latest_version() 
                    
                    if latest_version:
                        last_no = latest_version.version_no
                    else:
                        last_no = 0
                        
                    for version in language_exists.subtitleversion_set.all():
                        version.language = original_language
                        last_no += 1
                        version.version_no = last_no
                        version.save()

                    language_exists.delete()
                except ObjectDoesNotExist:
                    pass
                
                original_language.language = video_language
                original_language.save()
        else:
            #original_language always exists, but...
            try:
                language_exists = video.subtitlelanguage_set.get(language=video_language)
                language_exists.is_original = True
                language_exists.save()
            except ObjectDoesNotExist:
                original_language = SubtitleLanguage()
                original_language.language = video_language
                original_language.is_original = True
                original_language.video = video
                original_language.save()

    def _best_existing(self, languages):
        for l in languages:
            # choosing first forked SL that has no dependent languages.
            if not l.is_dependent() and l.subtitlelanguage_set.count() == 0:
                return l
        return None

    def _find_appropriate_language(self, video, language_code):
        language = video.subtitle_language(language_code)
        if not language:
            language = SubtitleLanguage(
                video=video, is_original=False, is_forked=True)
        language.language = language_code
        language.save()
        return language

    def save_subtitles(self, parser, video=None, language=None, update_video=True):
        video = video or self.cleaned_data['video']
        
        if not video.has_original_language():
            self._save_original_language(
                video, self.cleaned_data['video_language'])
        
        language = language or self._find_appropriate_language(video, self.cleaned_data['language'])
        language = save_subtitle(video, language, parser, self.user, update_video)
   
        return language

    def get_errors(self):
        output = {}
        for key, value in self.errors.items():
            output[key] = '/n'.join([force_unicode(i) for i in value])
        return output
    
class SubtitlesUploadForm(SubtitlesUploadBaseForm):
    subtitles = forms.FileField()
    is_complete = forms.BooleanField(initial=True, required=False)
    
    def clean_subtitles(self):
        subtitles = self.cleaned_data['subtitles']
        if subtitles.size > KB_SIZELIMIT * 1024:
            raise forms.ValidationError(_(
                    u'File size should be less {0} kb'.format(KB_SIZELIMIT)))
        parts = subtitles.name.split('.')
        if len(parts) < 1 or not parts[-1].lower() in ['srt', 'ass', 'ssa', 'xml', 'sbv']:
            raise forms.ValidationError(_(u'Incorrect format. Upload .srt, .ssa, .sbv or .xml (TTML  format)'))
        try:
            text = subtitles.read()
            encoding = chardet.detect(text)['encoding']
            if not encoding:
                raise forms.ValidationError(_(u'Can not detect file encoding'))
            if not self._get_parser(subtitles.name)(force_unicode(text, encoding)):
                raise forms.ValidationError(_(u'Incorrect subtitles format'))
        except SubtitleParserError, e:
            raise forms.ValidationError(e)
        subtitles.seek(0)
        return subtitles
    
    def _get_parser(self, filename):
        end = filename.split('.')[-1].lower()
        if end == 'srt':
            return SrtSubtitleParser
        if end in ['ass', 'ssa']:
            return SsaSubtitleParser
        if end == 'xml':
            return TtmlSubtitleParser
        if end == 'sbv':
            return SbvSubtitleParser
        
    def save(self):
        subtitles = self.cleaned_data['subtitles']
        text = subtitles.read()
        parser = self._get_parser(subtitles.name)(force_unicode(text, chardet.detect(text)['encoding']))        
        sl = self.save_subtitles(parser, update_video=False)
        is_complete = self.cleaned_data.get('is_complete')
        sl.is_complete = is_complete
        if len(sl.latest_version().subtitles()) > 0:
            # this will eventually get updated on the async test
            # but if it takes too long on html file uplods
            # then users will not see the language added which is very
            # confusing from a UI point of view
            sl.had_version = sl.has_version = True
        sl.save()
        video_changed_tasks.delay(sl.video_id, sl.latest_version().id)
        return sl
 
class PasteTranscriptionForm(SubtitlesUploadBaseForm):
    subtitles = forms.CharField()

    def save(self):
        subtitles = self.cleaned_data['subtitles']
        parser = TxtSubtitleParser(subtitles)       
        language = self.save_subtitles(parser)
        if language.is_original:
            language.video.subtitlelanguage_set.exclude(pk=language.pk).update(is_forked=True)
        return language
    
class UserTestResultForm(forms.ModelForm):
    
    class Meta:
        model = UserTestResult
        exclude = ('browser',)
        
    def save(self, request):
        obj = super(UserTestResultForm, self).save(False)
        obj.browser = request.META.get('HTTP_USER_AGENT', 'empty HTTP_USER_AGENT')
        obj.save()
        return obj

class VideoForm(forms.Form):
    video_url = forms.URLField(verify_exists=True)
    
    def __init__(self, user=None, *args, **kwargs):
        if user and not user.is_authenticated():
            user = None
        self.user = user
        super(VideoForm, self).__init__(*args, **kwargs)
        self.fields['video_url'].widget.attrs['class'] = 'main_video_form_field'
    
    def clean_video_url(self):
        video_url = self.cleaned_data['video_url']
        
        if video_url:
            try:
                video_type = video_type_registrar.video_type_for_url(video_url)
            except VideoTypeError, e:
                raise forms.ValidationError(e)
            if not video_type:
                for d in video_type_registrar.domains:
                    if d in video_url:
                        raise forms.ValidationError(mark_safe(_(u"""Please try again with a link to a video page. 
                        <a href="mailto:%s">Contact us</a> if there's a problem.""") % settings.FEEDBACK_EMAIL))
                    
                raise forms.ValidationError(mark_safe(_(u"""You must link to a video on a compatible site (like YouTube) or directly to a
                    video file that works with HTML5 browsers. For example: http://mysite.com/myvideo.ogg or http://mysite.com/myipadvideo.m4v
                    <a href="mailto:%s">Contact us</a> if there's a problem.""") % settings.FEEDBACK_EMAIL))
                             
            else:
                self._video_type = video_type
            
        return video_url
    
    def save(self):
        video_url = self.cleaned_data['video_url']
        obj, created = Video.get_or_create_for_url(video_url, self._video_type, self.user)
        self.created = created
        return obj

youtube_user_url_re = re.compile(r'^(http://)?(www.)?youtube.com/user/(?P<username>[a-zA-Z0-9]+)/?.*$')

class AddFromFeedForm(forms.Form, AjaxForm):
    VIDEOS_LIMIT = 10
    
    youtube_feed_url_pattern =  'https://gdata.youtube.com/feeds/api/users/%s/uploads'
    usernames = UsernameListField(required=False, label=_(u'Youtube usernames'), help_text=_(u'<span class="hint">Enter usernames separated by comma.</span>'))
    youtube_user_url = StripRegexField(youtube_user_url_re, required=False, label=_(u'Youtube page link.'), 
                                       help_text=_(u'<span class="hint">For example: http://www.youtube.com/user/username</span>'))
    feed_url = FeedURLField(required=False, help_text=_(u'<span class="hint">Supported: Youtube, Vimeo, Blip or Dailymotion. Only supported sites added.</span>'))
    save_feed = forms.BooleanField(required=False, label=_(u'Save feed'), help_text=_(u'<span class="hint checkbox_hint">Choose this if you wish to add videos from this feed in the future. Only valid RSS feeds will be saved.</span>'))
    
    def __init__(self, user, *args, **kwargs):
        if not user.is_authenticated():
            user = None
        self.user = user
        super(AddFromFeedForm, self).__init__(*args, **kwargs)
        
        self.yt_service = YouTubeService()
        self.video_types = [] #tuples: (video_type, video_info)
        self.feed_urls = [] #tuples: (feed_url, last_saved_entry_url)
        self.video_limit_routreach = False 
        
    def clean_feed_url(self):
        url = self.cleaned_data.get('feed_url', '')
        
        if url:
            self.parse_feed_url(url)
                
        return url
    
    def clean_youtube_user_url(self):
        url = self.cleaned_data.get('youtube_user_url', '').strip()
        
        if url:
            username = youtube_user_url_re.match(url).groupdict()['username']
            url = self.youtube_feed_url_pattern % str(username)
            self.parse_feed_url(url)
        return url
        
    def clean_usernames(self):
        usernames = self.cleaned_data.get('usernames', [])
        for username in usernames:
            url = self.youtube_feed_url_pattern % str(username)
            self.parse_feed_url(url)
        return usernames
    
    def parse_feed_url(self, url):
        feed_parser = FeedParser(url)
        entry = ''
        
        try:
            for vt, info, entry in feed_parser.items():
                if vt:
                    self.video_types.append((vt, info))

                if len(self.video_types) >= self.VIDEOS_LIMIT:
                    self.video_limit_routreach = True
                    break  

            if feed_parser.feed.version:
                try:
                    self.feed_urls.append((url, entry and entry['link']))
                except KeyError:
                    raise forms.ValidationError(_(u'Sorry, we could not find a valid feed at the URL you provided. Please check the URL and try again.'))
                
        except FeedParserError, e:
            raise forms.ValidationError(e) 
    
    def save_feed_url(self, feed_url, last_entry_url):
        try:
            VideoFeed.objects.get(url=feed_url)
        except VideoFeed.DoesNotExist:
            vf = VideoFeed(url=feed_url)
            vf.user = self.user
            vf.last_link = last_entry_url
            vf.save()
                                                
    def save(self):
        if self.cleaned_data.get('save_feed'):
            for feed_url, last_entry_url in self.feed_urls:
                self.save_feed_url(feed_url, last_entry_url)
            
        for vt, info in self.video_types:
            video, created = Video.get_or_create_for_url(vt=vt, user=self.user)
            
        return len(self.video_types)
    
class FeedbackForm(forms.Form):
    email = forms.EmailField(required=False)
    message = forms.CharField(widget=forms.Textarea())
    error = forms.CharField(required=False, widget=forms.HiddenInput)
    captcha = ReCaptchaField(label=_(u'captcha'))
    
    def __init__(self, *args, **kwargs):
        hide_captcha = kwargs.pop('hide_captcha', False)
        super(FeedbackForm, self).__init__(*args, **kwargs)
        if hide_captcha:
            del self.fields['captcha']
    
    def send(self, request):
        email = self.cleaned_data['email']
        message = self.cleaned_data['message']
        error = self.cleaned_data['error']
        user_agent_data = u'User agent: %s' % request.META.get('HTTP_USER_AGENT')
        timestamp = u'Time: %s' % datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        version = u'Version: %s' % settings.PROJECT_VERSION
        commit = u'Commit: %s' % settings.LAST_COMMIT_GUID
        url = u'URL: %s' % request.META.get('HTTP_REFERER', '')
        user = u'Logged in: %s' % (request.user.is_authenticated() and request.user or u'not logged in')
        message = u'%s\n\n%s\n%s\n%s\n%s\n%s\n%s' % (message, user_agent_data, timestamp, version, commit, url, user)
        if error in ['404', '500']:
            message += u'\nPage type: %s' % error
            feedback_emails = [settings.FEEDBACK_ERROR_EMAIL]
        else:
            feedback_emails = settings.FEEDBACK_EMAILS
        headers = {'Reply-To': email} if email else None
        bcc = getattr(settings, 'EMAIL_BCC_LIST', [])
        if email:
            subject = '%s (from %s)' % (settings.FEEDBACK_SUBJECT, email)
        else:
            subject = settings.FEEDBACK_SUBJECT
        EmailMessage(subject, message, email, \
                         feedback_emails, headers=headers, bcc=bcc).send()
        
        if email:
            headers = {'Reply-To': settings.FEEDBACK_RESPONSE_EMAIL}
            body = render_to_string(settings.FEEDBACK_RESPONSE_TEMPLATE, {})
            email = EmailMessage(settings.FEEDBACK_RESPONSE_SUBJECT, body, \
                         settings.FEEDBACK_RESPONSE_EMAIL, [email], headers=headers, bcc=bcc)
            email.content_subtype = 'html'
            email.send()
                     
    def get_errors(self):
        from django.utils.encoding import force_unicode        
        output = {}
        for key, value in self.errors.items():
            output[key] = '/n'.join([force_unicode(i) for i in value])
        return output
    
class EmailFriendForm(MathCaptchaForm):
    from_email = forms.EmailField(label='From')
    to_emails = EmailListField(label='To')
    subject = forms.CharField()
    message = forms.CharField(widget=forms.Textarea())
    
    def send(self):
        subject = self.cleaned_data['subject']
        message = self.cleaned_data['message']
        from_email = self.cleaned_data['from_email']
        to_emails = self.cleaned_data['to_emails']
        send_mail(subject, message, from_email, to_emails)
