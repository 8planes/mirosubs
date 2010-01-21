from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import render_to_response
from django.template import RequestContext
from profiles.forms import EditProfileForm

@login_required
def my_profile(request):
    return profile(request, request.user.username)

def profile(request, user_id):
    try:
        user = User.objects.get(username=user_id)
    except User.DoesNotExist:
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise Http404
    profile = user.get_profile()
    # TODO: get user's activity
    if request.user == user:
        if request.method == 'POST':
            edit_profile_form = EditProfileForm(request.POST,
                                                instance=profile,
                                                files=request.FILES)
            if edit_profile_form.is_valid():
                edit_profile_form.save()
                request.user.message_set.create(message='Your profile has been updated.')
        else:
            edit_profile_form = EditProfileForm(instance=profile)
        return render_to_response('profiles/edit_profile.html', locals(),
                                  context_instance=RequestContext(request))
    else:
        return render_to_response('profiles/view_profile.html', locals(),
                                  context_instance=RequestContext(request))

            
            