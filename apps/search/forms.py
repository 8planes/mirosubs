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
    
    def __init__(self, request, *args, **kwargs):
        if 'sqs' in kwargs:
            sqs = kwargs['sqs']
            del kwargs['sqs']
        else:
            sqs = None
            
        super(SearchForm, self).__init__(*args, **kwargs)
        self.user_langs = get_user_languages_from_request(request)
        
        if sqs:
            facet_data = sqs.facet('video_language').facet('languages').facet_counts()
            video_langs_data = facet_data['fields']['video_language']
            self.fields['video_lang'].choices = self._make_choices_from_faceting(video_langs_data)
    
            langs_data = facet_data['fields']['languages']
            self.fields['langs'].choices = self._make_choices_from_faceting(langs_data)
        else:
            choices = list(get_simple_languages_list())
            self.fields['langs'].choices = choices
            self.fields['video_lang'].choices = choices
    
    def get_display_views(self):
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
                choices.append((lang, ALL_LANGUAGES_NAMES[lang], val))
            except KeyError:
                pass

        choices.sort(key=lambda item: item[-1], reverse=True)
        
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
            qs = qs.filter(video_language__exact=video_language)
        
        if langs:
            qs = qs.filter(languages=langs)
        
        if ordering:
            qs = qs.order_by('-' + ordering)
        else:
            qs = qs.order_by('-languages_count')
            
        return qs
