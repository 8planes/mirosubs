from django.contrib.auth.models import User
from socialauth.lib import oauthtwitter
from socialauth.models import OpenidProfile as UserAssociation, AuthMeta
import random

class OpenIdBackend:
    def authenticate(self, openid_key, request, provider):
        try:
            assoc = UserAssociation.objects.get(openid_key = openid_key)
            return assoc.user
        except UserAssociation.DoesNotExist:
            #fetch if openid provider provides any simple registration fields
            nickname = None
            email = None
            if request.openid and request.openid.sreg:
                email = request.openid.sreg.get('email')
                nickname = request.openid.sreg.get('nickname')
            elif request.openid and request.openid.ax:
                if provider == 'Google':
                    email = request.openid.ax.get('http://axschema.org/contact/email')
                    email = email.pop()
                else:
                    email = request.openid.ax.get('email')
                    nickname = request.openid.ax.get('nickname')
 
            if nickname is None :
                if email:
                    nickname = email.split('@')[0]
                else:
                    nickname =  ''.join([random.choice('abcdefghijklmnopqrstuvwxyz') for i in xrange(10)])
            if email is None :
                valid_username = False
                email =  None #'%s@example.openid.com'%(nickname)
            else:
                valid_username = True
            name_count = User.objects.filter(username__startswith = nickname).count()
            if name_count:
                username = '%s%s'%(nickname, name_count + 1)
                user = User.objects.create_user(username,email or '')
            else:
                user = User.objects.create_user(nickname,email or '')
            user.save()
 
            #create openid association
            assoc = UserAssociation()
            assoc.openid_key = openid_key
            assoc.user = user
            if email:
                assoc.email = email
            if nickname:
                assoc.nickname = nickname
            if valid_username:
                assoc.is_username_valid = True
            assoc.save()
 
            #Create AuthMeta
            auth_meta = AuthMeta(user = user, provider = provider)
            auth_meta.save()
            return user
 
    def get_user(self, user_id):
        try:
            user = User.objects.get(pk = user_id)
            return user
        except User.DoesNotExist:
            return None