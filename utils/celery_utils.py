from celery.task import task as task_decorator
from celery.app import app_or_default
from celery.task.base import extract_exec_options

TaskBase = app_or_default().Task

class Task(TaskBase):
    """
    This Task class does not close publisher connection and publisher is catched.
    We don't want create new connection every time, because it is slowly.
    """
    
    @classmethod
    def apply_async(self, args=None, kwargs=None, countdown=None,
            eta=None, task_id=None, publisher=None, connection=None,
            connect_timeout=None, router=None, expires=None, queues=None,
            **options):
        
        router = self.app.amqp.Router(queues)
        conf = self.app.conf

        if conf.CELERY_ALWAYS_EAGER:
            return self.apply(args, kwargs, task_id=task_id)

        options.setdefault("compression",
                           conf.CELERY_MESSAGE_COMPRESSION)
        options = dict(extract_exec_options(self), **options)
        options = router.route(options, self.name, args, kwargs)
        exchange = options.get("exchange")
        exchange_type = options.get("exchange_type")
        expires = expires or self.expires

        publish = publisher or self.get_publisher(connection,
                                                  exchange=exchange,
                                                  exchange_type=exchange_type)
        evd = None
        if conf.CELERY_SEND_TASK_SENT_EVENT:
            evd = self.app.events.Dispatcher(channel=publish.channel,
                                             buffer_while_offline=False)

        task_id = publish.delay_task(self.name, args, kwargs,
                                     task_id=task_id,
                                     countdown=countdown,
                                     eta=eta, expires=expires,
                                     event_dispatcher=evd,
                                     **options)

        return self.AsyncResult(task_id)
            
    @classmethod
    def get_publisher(self, connection=None, exchange=None,
            connect_timeout=None, exchange_type=None, **options):
        
        if not hasattr(self, '_publisher'):
            self._publisher = super(TaskBase, self).get_publisher(connection, exchange,
                    connect_timeout, exchange_type, **options)

        return self._publisher
            
def task(*args, **kwargs):
    kwargs.setdefault('base', Task)
    return task_decorator(*args, **kwargs)