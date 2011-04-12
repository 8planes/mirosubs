from django.contrib.auth.models import User
from django.conf import settings
from django.contrib.auth.backends import ModelBackend
from socialauth.lib import oauthtwitter, facebook
from socialauth.models import OpenidProfile as UserAssociation, TwitterUserProfile, FacebookUserProfile, AuthMeta
#from django.contrib.auth import models as auth_models
    
import cgi
import urllib, urllib2
import simplejson 

from datetime import datetime
import random

TWITTER_CONSUMER_KEY = getattr(settings, 'TWITTER_CONSUMER_KEY', '')
TWITTER_CONSUMER_SECRET = getattr(settings, 'TWITTER_CONSUMER_SECRET', '')
FACEBOOK_API_KEY = getattr(settings, 'FACEBOOK_API_KEY', '')
FACEBOOK_APP_SECRET = getattr(settings, 'FACEBOOK_APP_SECRET', '')

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
        
        try:
            user_profile = TwitterUserProfile.objects.get(screen_name = screen_name)
            user = user_profile.user
            return User.objects.get(pk=user.pk)
        except (TwitterUserProfile.DoesNotExist, User.DoesNotExist):
            #Create new user
            same_name_count = User.objects.filter(username__startswith = screen_name).count()
            if same_name_count:
                username = '%s%s' % (screen_name, same_name_count + 1)
            else:
                username = screen_name
            user = User(username =  username)
            temp_password = User.objects.make_random_password(length=12)
            user.set_password(temp_password)
            name_data = userinfo.name.split()
            try:
                first_name, last_name = name_data[0], ' '.join(name_data[1:])
            except:
                first_name, last_name =  screen_name, ''
            user.first_name, user.last_name = first_name, last_name
            user.email = '%s@twitteruser.%s.com'%(userinfo.screen_name, settings.SITE_NAME)
            user.save()
            userprofile = TwitterUserProfile(user = user, screen_name = screen_name)
            userprofile.access_token = access_token.key
            userprofile.url = userinfo.url
            userprofile.location = userinfo.location
            userprofile.description = userinfo.description
            userprofile.profile_image_url = userinfo.profile_image_url
            userprofile.save()
            auth_meta = AuthMeta(user=user, provider='Twitter').save()
            return user

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except:
            return None
        

class FacebookBackend:
    def authenticate(self, fb_access_token):
        '''authenticates token by requesting user information from facebook
        '''
        try:
            graph = facebook.GraphAPI(fb_access_token)
            userinfo = graph.get_object("me")
        except:
            # If we cannot get user info, user cannot be authenticated 
            raise

        fb_uid = userinfo['id']
        try:
            user_profile = FacebookUserProfile.objects.get(fb_uid=fb_uid)
            user = user_profile.user
            user_profile.access_token = fb_access_token
            return User.objects.get(pk=user.pk)
        except (FacebookUserProfile.DoesNotExist, User.DoesNotExist):
            fb_uid = userinfo['id']
            #Create new user
            try:
                fb_username = userinfo['username']
            except KeyError:
                #if username not set on facebook
                fb_username = userinfo['first_name']
            same_name_count = User.objects.filter(username__startswith = fb_username).count()
            if same_name_count:
                username = '%s%s' % (fb_username, same_name_count + 1)
            else:
                username = fb_username
            user = User(username =  username)
            temp_password = User.objects.make_random_password(length=12)
            user.set_password(temp_password)
            user.first_name, user.last_name = userinfo['first_name'], userinfo['last_name']
            user.email = '%s@facebook.%s.com'%(username, settings.SITE_NAME)
            user.save()
            image_url = 'http://graph.facebook.com/me/picture?type=large'+'&access_token='+fb_access_token
            userprofile = FacebookUserProfile(user = user, fb_uid = fb_uid, fb_username = fb_username, location = userinfo['location'])
            userprofile.access_token = fb_access_token
            userprofile.save()
            auth_meta = AuthMeta(user=user, provider='Facebook').save()
            return user

    def get_user(self,user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
