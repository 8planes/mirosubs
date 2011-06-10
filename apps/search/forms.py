from django import forms
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from utils.translation import get_languages_list
from utils.translation import get_user_languages_from_request

ALL_LANGUAGES = tuple((val, _(name))for val, name in settings.ALL_LANGUAGES)

class SearchForm(forms.Form):
    SORT_CHOICES = (
        ('languages_count', _(u'Most languages')),
        ('week_views', _(u'Most plays (this week)')),
        ('month_views', _(u'Most plays (this month)')),
        ('total_views', _(u'Most plays (all time)')),
    )
    DISPLAY_CHOICES = (
        ('all', _(u'all')),
        ('thumbnails', _(u'thumbnails')),
    )
    q = forms.CharField(required=False, label=_(u'query'))
    sort = forms.ChoiceField(choices=SORT_CHOICES, required=False, initial='languages_count',
                             label=_(u'Sort By'))
    langs = forms.ChoiceField(choices=ALL_LANGUAGES, required=False, label=_(u'languages'),
                              help_text=_(u'Left blank for any language'))
    video_lang = forms.ChoiceField(choices=ALL_LANGUAGES, required=False, label=_(u'video language'),
                              help_text=_(u'Left blank for any language'))
    display = forms.ChoiceField(choices=DISPLAY_CHOICES, required=False, initial='all')
    
    def __init__(self, request, *args, **kwargs):
        super(SearchForm, self).__init__(*args, **kwargs)
        choices = list(get_languages_list())
        self.user_langs = get_user_languages_from_request(request)
        choices[:0] = (
            ('my_langs', _(u'My languages')),
            ('', _(u'Any Language')),
            ('not_selected', 'Not ---'),
        )
        self.fields['langs'].choices = choices
        self.fields['video_lang'].choices = choices
        
    def search_qs(self, qs):
        q = self.cleaned_data.get('q')
        ordering = self.cleaned_data.get('sort', '')
        langs = self.cleaned_data.get('langs')
        video_language = self.cleaned_data.get('video_lang')
        
        qs = qs.auto_query(q)
        
        if video_language:
            if video_language == 'my_langs':
                qs = qs.filter(video_language__in=self.user_langs)
            elif video_language == 'not_selected' and langs not in ['', 'not_selected']:
                if langs == 'my_langs':
                    qs = qs.exclude(video_language__in=self.user_langs)
                else:
                    qs = qs.exclude(video_language=langs)
            else:
                qs = qs.filter(video_language=video_language)
        
        if langs:
            if langs == 'my_langs':
                qs = qs.filter(languages__in=self.user_langs)
            elif langs == 'not_selected' and video_language not in ['', 'not_selected']:
                if video_language == 'my_langs':
                    qs = qs.exclude(languages__in=self.user_langs)
                else:
                    qs = qs.exclude(languages=langs)
            else:
                qs = qs.filter(languages=langs)
        
        if ordering:
            qs = qs.order_by('-' + ordering)
        else:
            qs = qs.order_by('-languages_count')
        
        #video_langs = qs.facet('video_language').facet_counts()['fields']['video_language']
        #print video_langs
        #self.fields['video_lang'].choices = tuple(() for l in video_langs[:10])
        
        return qs
