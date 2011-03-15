from django.core.management.base import BaseCommand
from teams.models import TeamVideoLanguage, TeamVideo
from django.conf import settings

class Command(BaseCommand):
    help = 'Update TeamVideoLanguage for selected languages'
    args = '[language ...]'
    
    def handle(self, *langs, **kwargs):
        available_languages = [item[0] for item in settings.ALL_LANGUAGES]
        
        for l in langs:
            if l in available_languages:
                print 'Update language %s ...' % l  
                for tv in TeamVideo.objects.all():
                    TeamVideoLanguage.update(tv, l)
                    
            else:
                print 'Language %s does not exist in settings' % l