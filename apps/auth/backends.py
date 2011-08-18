from auth.models import CustomUser as User
from django.contrib.auth.models import User as AuthUser
from django.conf import settings
from django.contrib.auth.backends import ModelBackend

from socialauth.lib import oauthtwitter
from socialauth.models import OpenidProfile as UserAssociation, TwitterUserProfile, FacebookUserProfile, AuthMeta

import random

TWITTER_CONSUMER_KEY = getattr(settings, 'TWITTER_CONSUMER_KEY', '')
TWITTER_CONSUMER_SECRET = getattr(settings, 'TWITTER_CONSUMER_SECRET', '')
FACEBOOK_API_KEY = getattr(settings, 'FACEBOOK_API_KEY', '')
FACEBOOK_API_SECRET = getattr(settings, 'FACEBOOK_API_SECRET', '')
FACEBOOK_REST_SERVER = getattr(settings, 'FACEBOOK_REST_SERVER', 'http://api.facebook.com/restserver.php')

class CustomUserBackend(ModelBackend):
    
    def authenticate(self, username=None, password=None):
        try:
            user = User.objects.get(username=username, is_active=True)
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            return None
        
    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

class OpenIdBackend:
    def authenticate(self, openid_key, request, provider):
        try:
            assoc = UserAssociation.objects.get(openid_key = openid_key)
            if assoc.user.is_active:
                return assoc.user
            else:
                return
        except UserAssociation.DoesNotExist:
            #fetch if openid provider provides any simple registration fields
            nickname = None
            email = None
            if request.openid and request.openid.sreg:
                email = request.openid.sreg.get('email')
                nickname = request.openid.sreg.get('nickname')
            elif request.openid and request.openid.ax:
                if provider in ('Google', 'Yahoo'):
                    email = request.openid.ax.get('http://axschema.org/contact/email')
                    email = email.pop()
                else:
                    try:
                        email = request.openid.ax.get('email')
                    except KeyError:
                        pass
                    
                    try:                      
                        nickname = request.openid.ax.get('nickname')
                    except KeyError:
                        pass
                    
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
            name_count = AuthUser.objects.filter(username__startswith = nickname).count()

            if name_count:
                username = '%s%s'%(nickname, name_count + 1)
                user = User.objects.create_user(username,email or '')
            else:
                user = User.objects.create_user(nickname,email or '')
            user.save()
 
            #create openid association
            assoc = UserAssociation()
            assoc.openid_key = openid_key
            assoc.user = user#AuthUser.objects.get(pk=user.pk)
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

from urllib import urlopen
from django.core.files.base import ContentFile

class TwitterBackend:
    """TwitterBackend for authentication
    """
    def authenticate(self, access_token):
        '''authenticates the token by requesting user information from twitter
        '''
        twitter = oauthtwitter.OAuthApi(TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET, access_token)

        try:
            userinfo = twitter.GetUserInfo()
        except:
            # If we cannot get the user information, user cannot be authenticated
            raise

        screen_name = userinfo.screen_name
        img_url = userinfo.profile_image_url
        
        try:
            user_profile = TwitterUserProfile.objects.get(screen_name = screen_name)
            if user_profile.user.is_active:
                return user_profile.user
            else:
                return        
        except TwitterUserProfile.DoesNotExist:
            #Create new user
            same_name_count = User.objects.filter(username__startswith = screen_name).count()
            if same_name_count:
                username = '%s%s' % (screen_name, same_name_count + 1)
            else:
                username = screen_name
            username = '@'+username
            
            name_count = AuthUser.objects.filter(username__startswith = username).count()
                
            if name_count:
                username = '%s%s'%(username, name_count + 1)
                            
            user = User(username =  username)
            temp_password = User.objects.make_random_password(length=12)
            user.set_password(temp_password)
            name_data = userinfo.name.split()
            try:
                first_name, last_name = name_data[0], ' '.join(name_data[1:])
            except:
                first_name, last_name =  screen_name, ''
            user.first_name, user.last_name = first_name, last_name
            if img_url:
                img = ContentFile(urlopen(img_url).read())
                name = img_url.split('/')[-1]
                user.picture.save(name, img, False)            
            #user.email = '%s@twitteruser.%s.com'%(userinfo.screen_name, settings.SITE_NAME)
            user.save()
            userprofile = TwitterUserProfile(user = user, screen_name = screen_name)
            userprofile.access_token = access_token.key
            userprofile.url = userinfo.url
            userprofile.location = userinfo.location
            userprofile.description = userinfo.description
            userprofile.profile_image_url = userinfo.profile_image_url
            userprofile.save()
            AuthMeta(user=user, provider='Twitter').save()
            return user

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except:
            return None
        

class FacebookBackend:
    def authenticate(self, facebook, request):
        facebook.check_session(request)
        user_info = facebook.users.getInfo([facebook.uid], ['first_name', 'last_name', 'pic_square'])[0]

        username = user_info['first_name']
        try:
            user_profile = FacebookUserProfile.objects.get(user__is_active=True, facebook_uid=user_info['uid'])
            if user_profile.user.is_active:
                return user_profile.user
            else:
                return None
        except FacebookUserProfile.DoesNotExist:
            name_count = AuthUser.objects.filter(username__istartswith=username).count()
            if name_count:
                username = '%s%s' % (username, name_count + 1)

            user = User.objects.create(username=username)
            user.first_name = user_info['first_name']
            user.last_name = user_info['last_name']
            user.save()

            location = '' # TODO: Figure out how to get this from Facebook.  Maybe.

            fb_profile = FacebookUserProfile(facebook_uid=user_info['uid'], user=user,
                    profile_image_url=user_info['pic_square'], location=location)
            fb_profile.save()

            AuthMeta(user=user, provider='Facebook').save()
            return user

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except:
            return None
