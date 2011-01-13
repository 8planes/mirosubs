from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.db.transaction import commit_on_success

class Command(BaseCommand):

    @commit_on_success
    def handle(self, *args, **kwargs):
        options = kwargs.get('options', {})
        fixtures = ['staging_users.json', 'staging_videos.json', 'staging_teams.json']
        for fx in fixtures:
            call_command('loaddata', fx, **options)