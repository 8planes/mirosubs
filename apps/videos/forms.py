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
from videos.models import Video, UserTestResult, SubtitleVersion, Subtitle, SubtitleLanguage
from django.core.mail import EmailMessage, send_mail
from django.conf import settings
from datetime import datetime
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _
import re
from utils import SrtSubtitleParser, SsaSubtitleParser, TtmlSubtitleParser, SubtitleParserError, SbvSubtitleParser, TxtSubtitleParser
import random
from django.utils.encoding import force_unicode
import chardet
from uuid import uuid4
from math_captcha.forms import MathCaptchaForm
from django.utils.safestring import mark_safe
from django.db.models import ObjectDoesNotExist
from videos.types import video_type_registrar, VideoTypeError
from videos.models import VideoUrl

ALL_LANGUAGES = [(val, _(name))for val, name in settings.ALL_LANGUAGES]

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
        video = self.cleaned_data['video']
        if video and not video.allow_video_urls_edit and not self.user.has_perm('videos.add_videourl'):
            raise forms.ValidationError(_('You have not permission add video URL for this video'))
        
        return self.cleaned_data
        
    def save(self, commit=True):
        obj = super(CreateVideoUrlForm, self).save(False)
        obj.type = self._video_type.abbreviation
        obj.added_by = self.user
        commit and obj.save()
        return obj
    
    def get_errors(self):
        output = {}
        for key, value in self.errors.items():
            output[key] = '/n'.join([force_unicode(i) for i in value])
        return output
    
class SubtitlesUploadBaseForm(forms.Form):
    language = forms.ChoiceField(choices=ALL_LANGUAGES, initial='en')
    video_language = forms.ChoiceField(choices=ALL_LANGUAGES, initial='en')
    video = forms.ModelChoiceField(Video.objects)

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(SubtitlesUploadBaseForm, self).__init__(*args, **kwargs)
        self.fields['language'].choices.sort(key=lambda item: item[1])
        
    def clean_video(self):
        video = self.cleaned_data['video']
        if video.is_writelocked:
            raise forms.ValidationError(_(u'Somebody is subtitling this video right now. Try later.'))
        return video
    
    def is_version_same(self, version, parser):
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
        
    def save_subtitles(self, parser):
        video = self.cleaned_data['video']
        
        key = str(uuid4()).replace('-', '')

        video._make_writelock(self.user, key)
        video.save()
        
        original_language = video.subtitle_language()
        video_language = self.cleaned_data['video_language']
        
        if original_language:
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
            
        language = video.subtitle_language(self.cleaned_data['language'])
        
        if not language:
            language = SubtitleLanguage(video=video, is_original=False, is_forked=True)
        
        language.language = self.cleaned_data['language']
        language.save()
        
        try:
            old_version = language.subtitleversion_set.all()[:1].get()    
            version_no = old_version.version_no + 1
        except ObjectDoesNotExist:
            old_version = None
            version_no = 0
        if not self.is_version_same(old_version, parser):
            
            version = SubtitleVersion(
                language=language, version_no=version_no,
                datetime_started=datetime.now(), user=self.user,
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

            version.save()
             
            language.was_complete = True
            language.is_complete = True
            language.save()
        
        video.release_writelock()
        video.save()
        
        return language

    def get_errors(self):
        output = {}
        for key, value in self.errors.items():
            output[key] = '/n'.join([force_unicode(i) for i in value])
        return output
    
class SubtitlesUploadForm(SubtitlesUploadBaseForm):
    subtitles = forms.FileField()
    
    def clean_subtitles(self):
        subtitles = self.cleaned_data['subtitles']
        if subtitles.size > 256*1024:
            raise forms.ValidationError(_(u'File size should be less 256 kb'))
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
        return self.save_subtitles(parser)
 
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
    
    def __init__(self, *args, **kwargs):
        super(VideoForm, self).__init__(*args, **kwargs)
        self.fields['video_url'].widget.attrs['class'] = 'main_video_form_field'
    
    def clean_video_url(self):
        video_url = self.cleaned_data['video_url']
        try:
            video_type = video_type_registrar.video_type_for_url(video_url)
        except VideoTypeError, e:
            raise forms.ValidationError(e)
        if not video_type:
            raise forms.ValidationError(mark_safe(_(u"""Universal Subtitles does not support that website or video format.
If you'd like to us to add support for a new site or format, or if you
think there's been some mistake, <a
href="mailto:%s">contact us</a>!""") % settings.FEEDBACK_EMAIL))             
        else:
            self._video_type = video_type
            
        return video_url
    
    def save(self):
        video_url = self.cleaned_data['video_url']
        obj, create = Video.get_or_create_for_url(video_url, self._video_type)
        return obj
    
class FeedbackForm(MathCaptchaForm):
    email = forms.EmailField(required=False)
    message = forms.CharField(widget=forms.Textarea())
    error = forms.CharField(required=False)
    
    def send(self, request):
        email = self.cleaned_data['email']
        message = self.cleaned_data['message']
        error = self.cleaned_data['error']
        user_agent_data = u'User agent: %s' % request.META.get('HTTP_USER_AGENT')
        timestamp = u'Time: %s' % datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        version = u'Version: %s' % settings.PROJECT_VERSION
        commit = u'Commit: %s' % settings.LAST_COMMIT_GUID
        url = u'URL: %s' % request.path_info
        user = u'Logged in: %s' % (request.user.is_authenticated() and request.user or u'not logged in')
        message = u'%s\n\n%s\n%s\n%s\n%s\n%s\n%s' % (message, user_agent_data, timestamp, version, commit, url, user)
        if error in ['404', '500']:
            message += u'\nPage type: %s' % error
            feedback_email = settings.FEEDBACK_ERROR_EMAIL
        else:
            feedback_email = settings.FEEDBACK_EMAIL
        headers = {'Reply-To': email} if email else None
        bcc = settings.EMAIL_BCC_LIST
        EmailMessage(settings.FEEDBACK_SUBJECT, message, email, \
                     [feedback_email ], headers=headers, bcc=bcc).send()
        
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

email_list_re = re.compile(
    r"""^(([-!#$%&'*+/=?^_`{}|~0-9A-Z]+(\.[-!#$%&'*+/=?^_`{}|~0-9A-Z]+)*|^"([\001-\010\013\014\016-\037!#-\[\]-\177]|\\[\001-011\013\014\016-\177])*")@(?:[A-Z0-9]+(?:-*[A-Z0-9]+)*\.)+[A-Z]{2,6},)+$""", re.IGNORECASE)

class EmailListField(forms.RegexField):
    default_error_messages = {
        'invalid': _(u'Enter valid e-mail addresses separated by commas.')
    }
    
    def __init__(self, max_length=None, min_length=None, *args, **kwargs):
        super(EmailListField, self).__init__(email_list_re, max_length, min_length, *args, **kwargs)
    
    def clean(self, value):
        if value:
            value = value and value.endswith(',') and value or value+','
        return super(EmailListField, self).clean(value)
    
class EmailFriendForm(MathCaptchaForm):
    from_email = forms.EmailField(label='From')
    to_emails = EmailListField(label='To')
    subject = forms.CharField()
    message = forms.CharField(widget=forms.Textarea())
    
    def send(self):
        subject = self.cleaned_data['subject']
        message = self.cleaned_data['message']
        from_email = self.cleaned_data['from_email']
        to_emails = self.cleaned_data['to_emails'].strip(',').split(',')
        send_mail(subject, message, from_email, to_emails)
