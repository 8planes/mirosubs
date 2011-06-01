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

#  Based on: http://www.djangosnippets.org/snippets/73/
#
#  Modified by Sean Reifschneider to be smarter about surrounding page
#  link context.  For usage documentation see:
#
#     http://www.tummy.com/Community/Articles/django-pagination/
from profiles.forms import SelectLanguageForm, EditUserEmailForm
from utils.rpc import RpcHttpResponse, add_request_to_kwargs, Error, Msg, RpcExceptionEvent
from utils.translation import get_user_languages_from_request
from django.utils.translation import ugettext as _

class ProfileApiClass(object):

    def fire_exception(self, user):
        raise Exception(1111)
    
    def select_languages(self, rdata, user):
        form = SelectLanguageForm(rdata)
        
        response = RpcHttpResponse()
        
        if form.is_valid():
            form.save(user, response)
            
        return response
    
    @add_request_to_kwargs
    def get_user_languages(self, user, request):
        return get_user_languages_from_request(request, with_names=True)
    
    def set_email(self, email, user):
        if not user.is_authenticated():
            return Error(_(u'You should be authenticated.'))
        
        form = EditUserEmailForm(dict(email=email), instance=user)
        if form.is_valid():
            form.save()
            return Msg(_(u'Your email was updated.'))
        else:
            return Error(form.errors['email'])