from django.contrib import admin

#add logging statistic display for SQS API usage
from statistic.log_methods import LogAdmin, LogFakeModel 
from kombu_backends.amazonsqs import SQSLoggingConnection

LogAdmin.register('SQS usage', SQSLoggingConnection.logger_backend)

admin.site.register(LogFakeModel, LogAdmin)