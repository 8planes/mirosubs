from auth.models import CustomUser
from django.contrib.auth.models import User
from django.conf import settings
from django.contrib.auth.backends import ModelBackend

from socialauth.lib import oauthtwitter
from socialauth.models import OpenidProfile as UserAssociation, TwitterUserProfile, FacebookUserProfile, AuthMeta
from socialauth.lib.facebook import get_user_info, get_facebook_signature

from datetime import datetime
import random

TWITTER_CONSUMER_KEY = getattr(settings, 'TWITTER_CONSUMER_KEY', '')
TWITTER_CONSUMER_SECRET = getattr(settings, 'TWITTER_CONSUMER_SECRET', '')
FACEBOOK_API_KEY = getattr(settings, 'FACEBOOK_API_KEY', '')
FACEBOOK_API_SECRET = getattr(settings, 'FACEBOOK_API_SECRET', '')

class CustomUserBackend(ModelBackend):
    
    def authenticate(self, username=None, password=None):
        try:
            user = User.objects.get(username=username)
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
            return User.objects.get(pk=assoc.user.pk)
        except (UserAssociation.DoesNotExist, User.DoesNotExist):
            #fetch if openid provider provides any simple registration fields
            nickname = None
            email = None
            if request.openid and request.openid.sreg:
                email = request.openid.sreg.get('email')
                nickname = request.openid.sreg.get('nickname')
            elif request.openid and request.openid.ax:
                email = request.openid.ax.get('email')
                nickname = request.openid.ax.get('nickname')
            if nickname is None :
                nickname =  ''.join([random.choice('abcdefghijklmnopqrstuvwxyz') for i in xrange(10)])
            if email is None :
                valid_username = False
                email =  '%s@%s.%s.com'%(nickname, provider, settings.SITE_NAME)
            else:
                valid_username = True                
            name_count = User.objects.filter(username__startswith = nickname).count()
            if name_count:
                username = '%s%s'%(nickname, name_count + 1)
                user = User.objects.create_user(username,email)
            else:
                user = User.objects.create_user(nickname,email)
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

def new_user(username, provider):
    "Creates a new user with a temporary password taking care of any same usernames"
    same_name_count = User.objects.filter(username__startswith = username).count()
    if same_name_count:
        username = '%s%s' % (username, same_name_count + 1)
    if provider == 'Twitter':
        username = '@'+username #for Twitter
    name_count = AuthUser.objects.filter(username__startswith = username).count()
    if name_count:
        username = '%s%s'%(username, name_count + 1)                        
    user = User(username =  username)
    temp_password = User.objects.make_random_password(length=12)
    user.set_password(temp_password)
    return user

class TwitterBackend:
    """TwitterBackend for authentication
    """
    def authenticate(self, access_token):
        """ authenticates the token by requesting user information from twitter """
        try:
            api = oauthtwitter.OAuthApi(TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET, access_token)
            userinfo = api.GetUserInfo()
        except:
            # If we cannot get the user information, user cannot be authenticated
            raise

        try:  
            user_profile = TwitterUserProfile.objects.get(screen_name = userinfo.screen_name)
            if user_profile.user.is_active:
                return user_profile.user
            else:
                return
        except TwitterUserProfile.DoesNotExist:
            #Create new user
            username = userinfo.screen_name
            user = new_user(username = username, provider = 'Twitter')
            name_data = userinfo.name.split()
            try:
                first_name, last_name = name_data[0], ' '.join(name_data[1:])
            except:
                first_name, last_name =  userinfo.screen_name, ''
            user.first_name, user.last_name = first_name, last_name
            user.save()
            img_url = userinfo.profile_image_url
            userprofile = TwitterUserProfile(user = user, screen_name = userinfo.screen_name)
            userprofile.access_token = access_token.key
            userprofile.url = userinfo.url
            userprofile.location = userinfo.location
            userprofile.description = userinfo.description
            userprofile.profile_image_url = userinfo.profile_image_url
            #user.email = '%s@Twitteruser.%s.com'%(userinfo.screen_name, settings.SITE_NAME)
            if img_url:
                img = ContentFile(urlopen(img_url).read())
                name = img_url.split('/')[-1]
                user.picture.save(name, img, False)
            
            userprofile.save()
            AuthMeta(user=user, provider='Twitter').save()
            return user

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except:
            return None
            
class FacebookBackend:
    """Facebook Backend for authentication
    """
    def authenticate(self, fb_access_token):
        """ authenticates the token by requesting user information from facebook """
        try:
            api = facebook.GraphAPI(fb_access_token)
            userinfo = api.get_object("me")
        except:
            # If we cannot get the user information, user cannot be authenticated
            raise
        # variables not initialise here
        try:
            user_profile = FacebookUserProfile.objects.get(fb_uid = userinfo['id'])
            if user_profile.user.is_active:
                return user_profile.user
            else:
                return
        except FacebookUserProfile.DoesNotExist:
            #Create new user
            try:
                username = userinfo['username']
            except KeyError:
                # if username not set on facebook
                username = userinfo['first_name']
                       
            user = new_user(username = username, provider = 'Facebook')
                       
            user.first_name, user.last_name = userinfo['first_name'], userinfo['last_name']
            #img_url = 'http://graph.facebook.com/me/picture?type=large'+'&fb_access_token='+ access_token
            user.save()
            userprofile = FacebookUserProfile(user = user, fb_uid = userinfo['id'], fb_username = username, location = userinfo['location'])
            userprofile.access_token = fb_access_token

            """if img_url:
                img = ContentFile(urlopen(img_url).read())
                name = img_url.split('/')[-1]
                user.picture.save(name, img, False)"""
       
        userprofile.save()
        AuthMeta(user=user, provider='Facebook').save()
        return user

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except:
            return None
