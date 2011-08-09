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
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from utils.translation import get_languages_list, get_simple_languages_list, get_user_languages_from_request
from videos.search_indexes import LanguageField

ALL_LANGUAGES = get_simple_languages_list()

class SearchForm(forms.Form):
    SORT_CHOICES = (
        ('languages_count', _(u'Most languages')),
        ('today_views', _(u'Views Today')),
        ('week_views', _(u'Views This Week')),
        ('month_views', _(u'Views This Month')),
        ('total_views', _(u'Total Views')),
    )
    q = forms.CharField(label=_(u'query'))
    sort = forms.ChoiceField(choices=SORT_CHOICES, required=False, initial='languages_count',
                             label=_(u'Sort By'))
    langs = forms.ChoiceField(choices=ALL_LANGUAGES, required=False, label=_(u'Subtitled Into'),
                              help_text=_(u'Left blank for any language'), initial='')
    video_lang = forms.ChoiceField(choices=ALL_LANGUAGES, required=False, label=_(u'Video In'),
                              help_text=_(u'Left blank for any language'), initial='')
    
    def __init__(self, *args, **kwargs):
        if 'sqs' in kwargs:
            sqs = kwargs['sqs']
            del kwargs['sqs']
        else:
            sqs = None
            
        super(SearchForm, self).__init__(*args, **kwargs)
        
        if sqs:
            facet_data = sqs.facet('video_language').facet('languages').facet_counts()
            video_langs_data = facet_data['fields']['video_language']
            self.fields['video_lang'].choices = self._make_choices_from_faceting(video_langs_data)
    
            langs_data = facet_data['fields']['languages']
            self.fields['langs'].choices = self._make_choices_from_faceting(langs_data)
        else:
            choices = list(get_simple_languages_list())
            choices.insert(0, ('', _('All Languages')))
            self.fields['langs'].choices = choices
            self.fields['video_lang'].choices = choices
    
    def get_display_views(self):
        if not hasattr(self, 'cleaned_data'):
            return 
        
        sort = self.cleaned_data.get('sort')
        
        if not sort:
            return
        
        if sort == 'today_views':
            return 'today'
        elif sort == 'week_views':
            return 'week'
        elif sort == 'month_views':
            return 'month'
        elif sort == 'total_views':
            return 'total'
    
    def _make_choices_from_faceting(self, data):
        choices = []
        
        ALL_LANGUAGES_NAMES = dict(get_simple_languages_list())
        
        for lang, val in data:
            lang = LanguageField.convert(lang)
            try:
                choices.append((lang, u'%s (%s)' % (ALL_LANGUAGES_NAMES[lang], val), val))
            except KeyError:
                pass

        choices.sort(key=lambda item: item[-1], reverse=True)
        choices = list((item[0], item[1]) for item in choices)
        choices.insert(0, ('', _('All Languages')))

        return choices
    
    @classmethod
    def apply_query(cls, q, qs):
        return qs.auto_query(q).filter_or(title=q)
    
    def search_qs(self, qs):
        q = self.cleaned_data.get('q')
        ordering = self.cleaned_data.get('sort', '')
        langs = self.cleaned_data.get('langs')
        video_language = self.cleaned_data.get('video_lang')
        
        qs = self.apply_query(q, qs)
        
        #aplly filtering
        if video_language:
            qs = qs.filter(video_language_exact=LanguageField.prepare_lang(video_language))
        
        if langs:
            qs = qs.filter(languages_exact=LanguageField.prepare_lang(langs))
        
        if ordering:
            qs = qs.order_by('-' + ordering)
        else:
            qs = qs.order_by('-languages_count')
            
        return qs
