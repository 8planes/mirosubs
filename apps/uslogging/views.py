from utils import render_to
from django.views.generic.list_detail import object_list
from uslogging.models import WidgetDialogLog
from django.contrib.admin.views.decorators import staff_member_required

@staff_member_required
def widget_logs(request):
    return object_list(
        request, 
        queryset=WidgetDialogLog.objects.order_by('-date_saved').all(),
        paginate_by=50,
        template_name='uslogging/widget_logs.html',
        template_object_name='log')

@render_to('uslogging/widget_log.html')
def widget_log(request, log_pk):
    return { 'log': WidgetDialogLog.objects.get(id=log_pk) }
