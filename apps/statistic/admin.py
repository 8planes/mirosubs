from django.contrib import admin
from statistic.models import SubtitleFetchCounters, VideoViewCounter
from django.views.generic.list_detail import object_list
from django.db import models

class SubtitleFetchCountersAdmin(admin.ModelAdmin):
    actions = None
    list_display = ['video', 'language', 'date', 'count']
    date_hierarchy = 'date'
    raw_id_fields = ['video']
    search_fields = ['video__title', 'videourl__url']
    readonly_fields = ['video', 'language', 'date']
    list_filter = ['language']
    
    def has_add_permission(self, request):
        return False

class VideoViewCounterAdmin(admin.ModelAdmin):
    actions = None
    list_display = ['video', 'date', 'count']
    date_hierarchy = 'date'
    raw_id_fields = ['video']
    search_fields = ['video__title', 'videourl__url']
    readonly_fields = ['video', 'date']
    
    def has_add_permission(self, request):
        return False

admin.site.register(SubtitleFetchCounters, SubtitleFetchCountersAdmin)    
admin.site.register(VideoViewCounter, VideoViewCounterAdmin)

#add logging statistic display for SQS API usage
from statistic.log_methods import LogAdmin, LogFakeModel 
from kombu_backends.amazonsqs import SQSLoggingConnection

LogAdmin.register('SQS usage', SQSLoggingConnection.logger_backend)

admin.site.register(LogFakeModel, LogAdmin)

#add logging statistic for migration data from Redis to MySQL
from statistic.pre_day_statistic import LoggerModelAdmin
from statistic import st_widget_view_statistic

class WidgetViewsMigrateStatistic(LoggerModelAdmin):
    logger = st_widget_view_statistic.log_to_redis
        
admin.site.register(WidgetViewsMigrateStatistic.model(), WidgetViewsMigrateStatistic)

#add ;ogging statistic for search index update
from utils.celery_search_index import LogEntry

class LogEntryAdmin(admin.ModelAdmin):
    rmodel = LogEntry
    
    @classmethod
    def fake_model(cls):
        class LogEntryFakeModel(models.Model):
            
            class Meta:
                managed = False
                verbose_name = cls.rmodel._meta['verbose_name']
                verbose_name_plural =  cls.rmodel._meta['verbose_name_plural']
        
        return LogEntryFakeModel
    
    def changelist_view(self, request, extra_context=None):
        opts = self.model._meta
        app_label = opts.app_label
        title = opts.verbose_name_plural
        
        qs = self.rmodel.objects.all()
        
        context = {
            'app_label': app_label,
            'title': title
        }
        return object_list(request, queryset=qs,
                           paginate_by=self.list_per_page,
                           template_name='statistic/log_entry_model_admin.html',
                           template_object_name='object',
                           extra_context=context)        
    
    def has_change_permission(self, request, obj=None):
        return not bool(obj)
            
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False
    
admin.site.register(LogEntryAdmin.fake_model(), LogEntryAdmin)