from django import forms
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from utils.translation import get_languages_list, get_simple_languages_list, get_user_languages_from_request
from videos.search_indexes import LanguageField

ALL_LANGUAGES = get_simple_languages_list()

class ModerationListSearchForm(forms.Form):
    SORT_CHOICES = (
        ("", "------"),
        ('revisions-newest', _(u'Newest')),
        ('revisions-oldest', _(u'Oldest')),
        ('video-title', _(u'Video TieleViews This Week')),

    )
    LANG_CHOICES = [
        ("", "------"),
        ("my-langs", "My languages"),
    ] + ALL_LANGUAGES
    
    
    q = forms.CharField(label=_(u'Video title?'), required=False)
    sort = forms.ChoiceField(choices=SORT_CHOICES, required=False, initial='languages_count',
                             label=_(u'Sort By'))
    to_langs = forms.ChoiceField(choices=LANG_CHOICES, required=False, label=_(u'Subtitled Into'),
                              help_text=_(u'Left blank for any language'), initial='')
    from_langs = forms.ChoiceField(choices=LANG_CHOICES, required=False, label=_(u'Video In'),
                              help_text=_(u'Left blank for any language'), initial='')
    
    def __init__(self,request,  *args, **kwargs):
        super(ModerationListSearchForm, self).__init__(request.GET, *args, **kwargs)
        self.user_langs = get_user_languages_from_request(request)

    def search_qs(self, qs=None):
        q = self.cleaned_data.get('q')
        ordering = self.cleaned_data.get('sort', '')
        to_langs = self.cleaned_data.get('to_langs')
        from_langs = self.cleaned_data.get('from_langs')


        if bool(q):
            qs = qs.auto_query(q).filter_or(title=q)

        if from_langs:
            if from_langs == "my-langs":
                qs = qs.filter(original_language__in=self.user_langs)
            else:
                qs = qs.filter(original_language=from_langs)

        if to_langs:
            if to_langs == "my-langs":
                qs = qs.filter(moderation_languages_names__in=self.user_langs)
            else:
                qs = qs.filter(moderation_languages_names=to_langs)

        if ordering:

            ordering_map= { 
                    "revisions-newest": "-latest_submission_date",
                    "revisions-oldest": "latest_submission_date",
                    "video-title": "video_title"
                    }
            criteria = ordering_map.get(ordering, None)
            print "odering : '%s' , criteria '%s' " % (ordering, criteria)
            if criteria:
                qs = qs.order_by(criteria)


        return qs
