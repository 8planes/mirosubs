from django.db import models
from django.utils.translation import ugettext_lazy as _

class Team(models.Model):
    APPLICATION = 1
    INVITATION_ONLY = 2
    OPEN = 3
    PRIVATE = 4
    MEMBERSHIP_POLICY_CHOICES = (
        (APPLICATION, _(u'Application')),
        (INVITATION_ONLY, _(u'Invitation Only')),
        (OPEN, _(u'Open')),
        (PRIVATE, _(u'Private'))
    )
    MEMBER_REMOVE = 1
    MANAGER_REMOVE = 2
    MEMBER_ADD = 3
    VIDEO_POLICY_CHOICES = (
        (MEMBER_REMOVE, _(u'Members add/remove')),
        (MANAGER_REMOVE, _(u'Managers add/remove')),
        (MEMBER_ADD, _(u'Members add videos'))
    )
    
    name = models.CharField(_(u'name'), max_length=250)
    description = models.TextField(_(u'description'))
    logo = models.ImageField(_(u'logo'), blank=True)
    membership_policy = models.IntegerField(_(u'membership policy'), choices=MEMBERSHIP_POLICY_CHOICES)
    video_policy = models.IntegerField(_(u'video policy'), choices=VIDEO_POLICY_CHOICES)
    is_visible = models.BooleanField(_(u'is public visible'), default=True)
    
    def __unicode__(self):
        return self.name