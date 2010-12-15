from django import forms
from django.utils.translation import ugettext_lazy as _
from django.conf import settings

ALL_LANGUAGES = tuple((val, _(name))for val, name in settings.ALL_LANGUAGES)

class SearchForm(forms.Form):
    TYPE_CHOICES = (
        ('title', _(u'Search Title only')),
        ('full_text', _(u'Search Full Text'))
    )
    SORT_TYPE_CHOICES = (
        ('asc', _(u'Ascending')),
        ('desc', _(u'Descending'))
    )
    SORT_CHOICES = (
        ('date', _(u'Date')),
        ('sub_fetch', _(u'Subtitles fetched')),
        ('page_loads', _(u'Page loads')),
        ('comments', _(u'Comments')),
        ('languages', _(u'Most languages')),
        #('last_edited', _(u'Last edited')),
        ('contributors', _(u'Contributors')),
        ('activity', _(u'Activity'))
    )
    
    q = forms.CharField(required=False, label=_(u'query'))
    type = forms.ChoiceField(choices=TYPE_CHOICES, required=False, initial='full_text', 
                             label=_(u'search type'), widget=forms.RadioSelect)
    st = forms.ChoiceField(choices=SORT_TYPE_CHOICES, required=False, initial='desc', 
                           label=_(u'sort order'), widget=forms.RadioSelect)
    sort = forms.ChoiceField(choices=SORT_CHOICES, required=False, initial='sub_fetch', label=_(u'sort type'))
    langs = forms.MultipleChoiceField(choices=ALL_LANGUAGES, required=False, label=_(u'languages'),
                                      help_text=_(u'Left blank for any language'))
    
    def __init__(self, user, *args, **kwargs):
        super(SearchForm, self).__init__(*args, **kwargs)
        self.fields['langs'].choices.sort(key=lambda item: item[1])
        self.user = user
        if user.is_authenticated():
            self.fields['langs'].choices[:0] = (
                ('my_langs', _(u'My Languages')),
            )
        
    def search_qs(self, qs):
        q = self.cleaned_data.get('q', '')
        ordering = self.cleaned_data.get('sort', 'page_loads')
        order_type = self.cleaned_data.get('st', 'asc')
        langs = self.cleaned_data.get('langs')
        type = self.cleaned_data.get('type', 'full_text')
        
        order_fields = {
            'date': 'created',
            'sub_fetch': 'subtitles_fetched_count',
            'page_loads': 'widget_views_count',
            'comments': 'comments_count',
            'languages': 'languages_count',
            'contributors': 'contributors_count',
            'activity': 'activity_count'
        }
        
        if q:
            if type == 'full_text':
                qs = qs.auto_query(q).highlight()
            else:
                qs = qs.filter(title=qs.query.clean(q))
        
        if langs:
            if 'my_langs' in langs and self.user.is_authenticated():
                del langs[langs.index('my_langs')]
                for l in self.user.userlanguage_set.values_list('language', flat=True):
                    if not l in langs:
                        langs.append(l)
                
            qs = qs.filter(languages__in=langs)

        qs = qs.order_by(('-' if order_type == 'desc' else '')+order_fields[ordering])
            
        return qs