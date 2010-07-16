from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from auth.models import CustomUser as User
from django.conf import settings

COMMENT_MAX_LENGTH = getattr(settings,'COMMENT_MAX_LENGTH', 3000)

class Comment(models.Model):
    content_type = models.ForeignKey(ContentType,
            related_name="content_type_set_for_%(class)s")
    object_pk = models.TextField('object ID')
    content_object = generic.GenericForeignKey(ct_field="content_type", fk_field="object_pk")
    user = models.ForeignKey(User)
    reply_to = models.ForeignKey('self', blank=True, null=True)
    content = models.TextField('comment', max_length=COMMENT_MAX_LENGTH)
    submit_date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ('-submit_date',)
        
    def __unicode__(self):
        return "%s: %s..." % (self.user.username, self.comment[:50])
    
    @classmethod
    def get_for_object(self, obj):
        if obj.pk:
            ct = ContentType.objects.get_for_model(obj)
            return self.objects.filter(content_type=ct, object_pk=obj.pk)
        else:
            return self.objects.none()
    
    def get_language(self):
        from videos.models import ProxyVideo, TranslationLanguage
        
        model_class = self.content_type.model_class()
        if issubclass(model_class, ProxyVideo):
            return 'Original'
        if issubclass(model_class, TranslationLanguage):
            return self.content_object.get_language_display()