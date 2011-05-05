from optparse import make_option

from django.core.management.base import BaseCommand
from teams.models import Team, TeamVideoLanguage

class Command(BaseCommand):
    help = 'Update All team metadata selected teams'
    args = '[team_slugs ...]'

    option_list = BaseCommand.option_list + (
        make_option('--all-teams', action='store', dest='all_teams',
            default=False, help='Resets all teams'
                'If set, will override the args param and clear all teams'),
    ) 

    def handle(self, *slugs, **kwargs):
        if kwargs['all_teams']:
            targets = Team.objects.all()
        else:
            targets = Team.objects.filter(slug__in=slugs)
        count = 0
        
        percent_printed = 0
        num = targets.count()
        print "%s teams to go " % num
        for team in targets.iterator():
            print "Updating team %s" % team.slug
            for tv in team.teamvideo_set.all():
                tv.update_team_video_language_pairs()
                TeamVideoLanguage.update(tv)
            percent = "%.2f %%" % (((count * 1.0) / num) * 100)
            if percent > percent_printed:
                percent_printed = percent
                print "Done %s%%" % (percent)
            
                
            
