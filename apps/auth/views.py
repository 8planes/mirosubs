# Universal Subtitles, universalsubtitles.org
# 
# Copyright (C) 2010 Participatory Culture Foundation
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
# 
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see 
# http://www.gnu.org/licenses/agpl-3.0.html.

from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.contrib.auth import authenticate
from django.contrib.auth import logout, login as auth_login
from auth.forms import CustomUserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _
from django.views.generic.simple import direct_to_template
from socialauth.models import AuthMeta, OpenidProfile, TwitterUserProfile, FacebookUserProfile
from utils.translation import get_user_languages_from_cookie
from auth.models import UserLanguage, CustomUser as User
from django.contrib.admin.views.decorators import staff_member_required
import facebook.djangofb as facebook
import base64, re

def login(request):
    redirect_to = request.REQUEST.get(REDIRECT_FIELD_NAME, '')
    return render_login(request, CustomUserCreationForm(label_suffix=""), 
                        AuthenticationForm(label_suffix=""), redirect_to)

def create_user(request):
    redirect_to = make_redirect_to(request)
    form = CustomUserCreationForm(request.POST, label_suffix="")
    if form.is_valid():
        new_user = form.save()
        user = authenticate(username=new_user.username,
                            password=form.cleaned_data['password1'])
        langs = get_user_languages_from_cookie(request)
        for l in langs:
            UserLanguage.objects.get_or_create(user=user, language=l)        
        auth_login(request, user)
        return HttpResponseRedirect(redirect_to)
    else:
        return render_login(request, form, AuthenticationForm(label_suffix=""), redirect_to)

@staff_member_required
def user_list(request):
    langs = request.GET.get('langs', None)
    if not langs:
        return render_to_response(
            'auth/user_list.html',
            context_instance=RequestContext(request))
    else:
        langs = re.split('[, ]+', langs)
        user_ids = set()
        users = User.objects.filter(userlanguage__language__in=langs).distinct()
        return render_to_response(
            'auth/user_list.csv',
            {'users': users},
            context_instance=RequestContext(request),
            mimetype="text/plain")

@login_required
def delete_user(request):
    if request.POST.get('delete'):
        user = request.user
        
        AuthMeta.objects.filter(user=user).delete()
        OpenidProfile.objects.filter(user=user).delete()
        TwitterUserProfile.objects.filter(user=user).delete()
        FacebookUserProfile.objects.filter(user=user).delete()
        
        user.is_active = False
        user.save()
        logout(request)
        messages.success(request, _(u'Your account was deleted.'))
        return HttpResponseRedirect('/')
    return direct_to_template(request, 'auth/delete_user.html')

def login_post(request):
    redirect_to = make_redirect_to(request)
    form = AuthenticationForm(data=request.POST, label_suffix="")
    if form.is_valid():
        auth_login(request, form.get_user())
        if request.session.test_cookie_worked():
            request.session.delete_test_cookie()
        return HttpResponseRedirect(redirect_to)
    else:
        return render_login(request, CustomUserCreationForm(label_suffix=""), form, redirect_to)

# Helpers

def render_login(request, user_creation_form, login_form, redirect_to):
    redirect_to = redirect_to or '/'
    return render_to_response(
        'auth/login.html', {
            'creation_form': user_creation_form,
            'login_form' : login_form,
            REDIRECT_FIELD_NAME: redirect_to,
            }, context_instance=RequestContext(request))
        
def make_redirect_to(request):
    redirect_to = request.REQUEST.get(REDIRECT_FIELD_NAME, '')
    if not redirect_to or '//' in redirect_to or ' ' in redirect_to:
        return '/'
    else:
        return redirect_to

from socialauth.views import get_url_host
from django.core.urlresolvers import reverse
from django.conf import settings
from socialauth.lib import oauthtwitter2 as oauthtwitter
from django.http import HttpResponse
from oauth import oauth
from urllib2 import URLError
from django.utils.http import urlquote

def twitter_login(request, next=None):
    callback_url = None
    next = request.GET.get('next', next)
    if next is not None:
        callback_url = '%s%s?next=%s' % \
             (get_url_host(request),
             reverse("auth:twitter_login_done"), 
             urlquote(next))
    twitter = oauthtwitter.TwitterOAuthClient(settings.TWITTER_CONSUMER_KEY, settings.TWITTER_CONSUMER_SECRET)
    try: 
        request_token = twitter.fetch_request_token(callback_url)
    except URLError:
        messages.error(request, 'Problem with connect to Twitter. Try again.')
        return redirect('auth:login')        
    request.session['request_token'] = request_token.to_string()
    signin_url = twitter.authorize_token_url(request_token)
    return HttpResponseRedirect(signin_url)

def twitter_login_done(request):
    request_token = request.session.get('request_token', None)
    oauth_verifier = request.GET.get("oauth_verifier", None)

    # If there is no request_token for session,
    # Means we didn't redirect user to twitter
    if not request_token:
        # Redirect the user to the login page,
        # So the user can click on the sign-in with twitter button
        return HttpResponse("We didn't redirect you to twitter...")
    
    token = oauth.OAuthToken.from_string(request_token)
    
    # If the token from session and token from twitter does not match
    #   means something bad happened to tokens
    if token.key != request.GET.get('oauth_token', 'no-token'):
        del request.session['request_token']
        # Redirect the user to the login page
        return HttpResponse("Something wrong! Tokens do not match...")

    twitter = oauthtwitter.TwitterOAuthClient(settings.TWITTER_CONSUMER_KEY, settings.TWITTER_CONSUMER_SECRET)
    try:  
        access_token = twitter.fetch_access_token(token, oauth_verifier)
    except URLError:
        messages.error(request, 'Problem with connect to Twitter. Try again.')
        return redirect('auth:login')
    
    request.session['access_token'] = access_token.to_string()
    user = authenticate(access_token=access_token)
    
    # if user is authenticated then login user
    if user:
        auth_login(request, user)
    else:
        # We were not able to authenticate user
        # Redirect to login page
        del request.session['access_token']
        del request.session['request_token']
        return HttpResponseRedirect(reverse('auth:login'))

#    print('authenticated: {0}'.format(user.is_authenticated()))

    # authentication was successful, use is now logged in
    return HttpResponseRedirect(request.GET.get('next', settings.LOGIN_REDIRECT_URL))


# Facebook

def _facebook():
    '''Return a pyfacebook Facebook object with our current API information.'''
    return facebook.Facebook(settings.FACEBOOK_API_KEY, settings.FACEBOOK_SECRET_KEY,
                             app_id=settings.FACEBOOK_APP_ID, oauth2=True)


def _fb64_encode(s):
    '''Return a base64-encoded version of the string that's compatible with Facebook.

    Facebook's OAuth2 implementation requires that callback URLs not include "special
    characters".  The safest way to pass a callback URL is to base64 encode it.

    Unfortunately Facebook considers a '/' to be a "special character", so we have to
    tell Python's base64 module to base64 it with some alternate characters.

    See this StackOverflow answer for more information:
    http://stackoverflow.com/questions/4386691/facebook-error-error-validating-verification-code/5389447#5389447

    '''
    return base64.b64encode(s, ['-', '_'])

def _fb64_decode(s):
    return base64.b64decode(str(s), ['-', '_'])


def _fb_callback_url(request, fb64_next):
    '''Return the callback URL for the given request and eventual destination.'''
    return '%s%s' % (
        get_url_host(request),
        reverse("auth:facebook_login_done", kwargs={'next': fb64_next}))

def _fb_fallback_url(fb64_next):
    '''Return a fallback URL that we'll redirect to if the authentication fails.

    If the eventual target is the widget's close_window URL we'll just redirect them
    back to that to close the popup window.

    Otherwise we'll redirect them back to the login page, preserving their
    destination.

    '''
    final_target_url = _fb64_decode(fb64_next)
    if 'close_window' in final_target_url:
        return final_target_url
    else:
        return '%s?next=%s' % (reverse('auth:login'), final_target_url)


def facebook_login(request, next=None):
    next = request.GET.get('next', settings.LOGIN_REDIRECT_URL)
    callback_url = _fb_callback_url(request, _fb64_encode(next))

    fb = _facebook()
    request.facebook = fb
    signin_url = fb.get_login_url(next=callback_url)

    return HttpResponseRedirect(signin_url)

def facebook_login_done(request, next):
    # The next parameter we get here is base64'ed.
    fb64_next = next

    fallback_url = _fb_fallback_url(fb64_next)

    code = request.GET.get('code')
    if not code:
        # If there's no code, the user probably clicked "Don't Allow".
        # Redirect them to the fallback.
        return HttpResponseRedirect(fallback_url)

    callback_url = _fb_callback_url(request, fb64_next)

    fb = _facebook()
    fb.oauth2_access_token(code, callback_url)

    request.facebook = fb
    user = authenticate(facebook=fb, request=request)

    if user:
        # If authentication was successful, log the user in and then redirect them
        # to their (decoded) destination.
        auth_login(request, user)
        return HttpResponseRedirect(_fb64_decode(fb64_next))
    else:
        # We were not able to authenticate the user.
        # Redirect them to login page, preserving their destination.
        return HttpResponseRedirect(fallback_url)
