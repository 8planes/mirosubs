from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.contrib.auth import authenticate

def login(request):
    redirect_to = request.REQUEST.get(REDIRECT_FIELD_NAME, '')
    print 'redirect_to: ' + redirect_to
    return render_to_response("auth/login.html", {
        'creation_form': UserCreationForm(),
        'login_form': AuthenticationForm(),
        REDIRECT_FIELD_NAME: redirect_to
    }, context_instance=RequestContext(request))

def create_user(request):
    redirect_to = request.REQUEST.get(REDIRECT_FIELD_NAME, '')
    print 'redirect_to: ' + redirect_to
    form = UserCreationForm(request.POST)
    if form.is_valid():
        # Light security check -- make sure redirect_to isn't garbage.
        if not redirect_to or '//' in redirect_to or ' ' in redirect_to:
            redirect_to = '/'
        new_user = form.save()
        user = authenticate(username=new_user.username,
                            password=form.cleaned_data['password1'])
        from django.contrib.auth import login
        login(request, user)
        return HttpResponseRedirect(redirect_to)
    else:
        return render_to_response("auth/login.html", {
                'creation_form': form,
                'login_form': AuthenticationForm(),
                REDIRECT_FIELD_NAME: redirect_to
                }, context_instance=RequestContext(request))

def login_post(request):
    redirect_to = request.REQUEST.get(REDIRECT_FIELD_NAME, '')
    print 'redirect_to: ' + redirect_to
    form = AuthenticationForm(data=request.POST)
    if form.is_valid():
        # Light security check -- make sure redirect_to isn't garbage.
        if not redirect_to or '//' in redirect_to or ' ' in redirect_to:
            redirect_to = '/'
        from django.contrib.auth import login
        login(request, form.get_user())
        if request.session.test_cookie_worked():
            request.session.delete_test_cookie()
        return HttpResponseRedirect(redirect_to)
    else:
        return render_to_response(
            'auth/login.html', {
                'creation_form': UserCreationForm(),
                'login_form' : form,
                REDIRECT_FIELD_NAME: redirect_to,
                }, context_instance=RequestContext(request))
