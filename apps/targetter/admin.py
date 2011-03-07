from targetter.forms import MessageConfigForm
from targetter.models import MessageConfig
from django.contrib import admin

class MessageConfigAdmin(admin.ModelAdmin):
    list_display = ['__unicode__', 'example_page']
    form = MessageConfigForm
    
    def example_page(self, obj):
        return '<a href="%s">Instruction</a>' % obj.get_absolute_url()
    
    example_page.allow_tags = True
    
admin.site.register(MessageConfig, MessageConfigAdmin)