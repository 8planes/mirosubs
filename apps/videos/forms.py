from django import forms
from videos.models import Video

class VideoForm(forms.ModelForm):
    class Meta:
        model = Video
        exclude = ('video_id', 'view_count', 'owner',
                   # TODO: this is being set to false in the save method it 
                   # should just be in the form when the models are finished.
                   'allow_community_edits',
                   'writelock_time', 'writelock_owner', 'writelock_session_key',)
                   