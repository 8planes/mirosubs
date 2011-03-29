from optparse import make_option

from django.core.management.base import BaseCommand
from teams.models import TeamVideoLanguage, TeamVideo
from django.conf import settings

class Command(BaseCommand):
    help = 'Update TeamVideoLanguage for selected languages'
    args = '[language ...]'

    option_list = BaseCommand.option_list + (
        make_option('--alllangs', action='store', dest='all_langs',
            default=False, help='Resets all languages'
                'If set, will override the args param and clear all languages'),
    )

    def _get_all_available_languages(self):
        return  [item[0] for item in settings.ALL_LANGUAGES]

    def _clear_langs(self, requested_langs):
        available_languages = self._get_all_available_languages()
        for l in requested_langs:
            if l in available_languages:
                print 'Update language %s ...' % l  
                for tv in TeamVideo.objects.all():
                    TeamVideoLanguage.update(tv, l)
                    
            else:
                print 'Language %s does not exist in settings' % l
                
    def handle(self, *langs, **kwargs):
        if kwargs['all_langs']:
            langs = self._get_all_available_languages()
        return self._clear_langs(langs)
