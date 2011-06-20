from django.contrib import admin
from statistic.models import SubtitleFetchCounters, VideoViewCounter

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