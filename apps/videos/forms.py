from django import forms
from widget.models import Video

class VideoForm(forms.Form):
    video_url = forms.URLField()

        