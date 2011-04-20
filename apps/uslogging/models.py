from django.db import models

class WidgetDialogLog(models.Model):
    date_saved = models.DateTimeField(auto_now_add=True)
    draft_pk = models.IntegerField()
    log = models.TextField()
