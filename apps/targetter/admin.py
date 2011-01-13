from targetter.forms import MessageConfigForm
from targetter.models import MessageConfig
from django.contrib import admin

class MessageConfigAdmin(admin.ModelAdmin):
    form = MessageConfigForm
    
admin.site.register(MessageConfig, MessageConfigAdmin)