from django import forms
from models import Comment
from django.contrib.contenttypes.models import ContentType
from django.utils.encoding import force_unicode
from django.conf import settings

COMMENT_MAX_LENGTH = getattr(settings,'COMMENT_MAX_LENGTH',3000)

class CommentForm(forms.ModelForm):
    honeypot = forms.CharField(required=False,
                                    label=_('If you enter anything in this field '\
                                            'your comment will be treated as spam'))
    content = forms.CharField(label=_('Comment'), widget=forms.Textarea,
                                    max_length=COMMENT_MAX_LENGTH)
    
    class Meta:
        model = Comment
        fields = ('content', 'reply_to')
        
    def __init__(self, obj, *args, **kwargs):
        self.target_object = obj
        super(CommentForm, self).__init__(*args, **kwargs)
        ct = ContentType.objects.get_for_model(obj)
        self.fields['reply_to'].queryset = Comment.objects.filter(content_type=ct, object_pk=obj.pk)
    
    def clean_honeypot(self):
        """Check that nothing's been entered into the honeypot."""
        value = self.cleaned_data["honeypot"]
        if value:
            raise forms.ValidationError(self.fields["honeypot"].label)
        return value  
        
    def save(self, user, commit=True):
        obj = super(CommentForm, self).save()
        obj.user = user
        obj.content_object = self.target_object
        if commit:
            obj.save()
        return obj