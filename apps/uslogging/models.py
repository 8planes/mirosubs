from django.db import models
from sentry.models import GzippedDictField

class WidgetDialogLog(models.Model):
    date_saved = models.DateTimeField(auto_now_add=True)
    draft_pk = models.IntegerField()
    browser_id = models.IntegerField()
    log = models.TextField()

class WidgetDialogCall(models.Model):
    date_saved = models.DateTimeField(auto_now_add=True)
    browser_id = models.CharField(max_length=127)
    method = models.CharField(max_length=127)
    request_args = GzippedDictField()
