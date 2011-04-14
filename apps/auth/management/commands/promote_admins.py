from optparse import make_option
import json

import logging
logger = logging.getLogger(__name__)

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Makes sure that all admin users on auth/users/fixtures/_admins are admins'
    
    option_list = BaseCommand.option_list + (
        make_option('--email', action='store', dest='email',
            default=None, help='The email of a user to be promoted'
                'If set, will override the args param and clear all languages'),
        make_option('--pass', action='store', dest='new_password',
            default=None, help='A new passowrd to be changed - optional'
                ''),
        make_option('--userlist-path', action='store', dest='userlist_path',
            default=None, help='Where the json user list should be stored'
                ''),
    )

    def promote_user(self, email, new_password=None):
        users = User.objects.filter(email=email)
        processed = []
        for u in users:
            try:
                u.is_active = u.is_staff = u.is_superuser = True
                if new_password:
                    u.set_password(new_password)
                u.save()
                processed.append(u)
            except:
                logger.exception("failed to promote user", email)
        return processed

                
    def handle(self, *langs, **kwargs):
        processed = []
        if kwargs.get('email', None) is not None:
            processed  = self.promote_user(kwargs.get("email"), kwargs.get("new_password", None))

        else:    
            # no command line args, we should get the userlist-path
            users_data = json.load(open(kwargs['userlist_path']))
            for data in users_data:
                processed.append(self.promote_user(data['email'], data.get("new_password", None)))
        print "processed %s" %  processed
