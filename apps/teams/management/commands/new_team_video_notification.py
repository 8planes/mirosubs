from django.core.management.base import BaseCommand
from teams.models import TeamVideo, Team
from datetime import datetime, timedelta
from django.contrib.sites.models import Site
from utils import send_templated_email
from django.conf import settings

class Command(BaseCommand):
    help = u'Send email about new videos'
    domain = Site.objects.get_current().domain
        
    def handle(self, *langs, **kwargs):
        print u'Send notifications...'
        date = datetime.today() - timedelta(hours=24)
        qs = Team.objects.filter(teamvideo__created__gte=date).distinct()
        
        for team in qs:
            self.send_notification(team, date)
        
    def send_notification(self, team, date):
        team_videos = team.teamvideo_set.filter(created__gte=date)

        if not team_videos:
            return
        
        subject = u'New %s videos ready for subtitling!' % team

        qs = team.users.filter(changes_notification=True, is_active=True) \
            .filter(teammember__changes_notification=True)

        for user in qs:
            if not user.email:
                continue

            context = {
                'domain': self.domain,
                'user': user,
                'team': team,
                'team_videos': team_videos
            }
            send_templated_email(user.email, subject, 
                                 'teams/email_new_videos.html',
                                 context, fail_silently=not settings.DEBUG)  