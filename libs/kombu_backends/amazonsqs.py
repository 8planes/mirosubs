from kombu.transport import virtual
from boto.sqs.connection import SQSConnection
from django.conf import settings
from boto import exception as boto_exceptions
from utils import LogExceptionsMetaclass

LOG_AMAZON_BROKER = getattr(settings, 'LOG_AMAZON_BROKER', False)

try:
    from termcolor import cprint
except ImportError:
    def cprint(s, c):
        print s
    
from kombu.utils import cached_property
from Queue import Empty
from anyjson import serialize, deserialize

def pr(s):
    cprint(s, 'green')        

DEBUG = False
EVENT_QUEUE_NAME = 'celeryev'

#this is for logging requests to SQS API
from utils.redis_utils import default_connection
from statistic.log_methods import LogNativeMethodsMetaclass, RedisLogBackend

class SQSLoggingConnection(SQSConnection):
    __metaclass__ = LogNativeMethodsMetaclass
    
    logger_backend = RedisLogBackend(default_connection)    

if LOG_AMAZON_BROKER:
    DEFAULT_CONNECTION = SQSLoggingConnection
else:
    DEFAULT_CONNECTION = SQSConnection

class Channel(virtual.Channel):
    #set logging these exceptions in any method of class by LogExceptionsMetaclass
    __log_exceptions_logger_name = 'celery'
    __log_exceptions = (
        boto_exceptions.BotoClientError, 
        boto_exceptions.SDBPersistenceError,
        boto_exceptions.BotoServerError,
        AttributeError,
        LookupError,
        EnvironmentError,
        RuntimeError,
        SystemError,
        ValueError
    )
    __metaclass__ = LogExceptionsMetaclass
    
    
    Client = DEFAULT_CONNECTION
    
    DOT_REPLECEMENT = '___'
    supports_fanout = False

    def __init__(self, connection, **kwargs):
        self.queue_prefix = connection.client.virtual_host or ''
        self.queue_cache = {}
        super(Channel, self).__init__(connection, **kwargs)

    def _lookup(self, exchange, routing_key, default="ae.undeliver"):
        """Find all queues matching `routing_key` for the given `exchange`.

        Returns `default` if no queues matched.

        """
        DEBUG and pr('_lookup: %s, %s' % (exchange, routing_key))
        queues = []
        
        #this is a hack for event sending
        #I just send it to all queues  with celeryev
        #In redis backend it looks like same way, but all queues are saved in set
        #but they are saved in _queue_bind witch is called only if supports_fanout == True
        if exchange == EVENT_QUEUE_NAME:
            for q in self.client.get_all_queues():
                parts = q.name.split(self.DOT_REPLECEMENT)
                if parts[0] == self.queue_prefix and parts[1] == EVENT_QUEUE_NAME:
                    queues.append(self.DOT_REPLECEMENT.join(parts[1:]))
        
        if queues:
            return queues
        
        return super(Channel, self)._lookup(exchange, routing_key, default)
    
    def _get(self, queue, timeout=None):
        """Get next message from `queue`."""
        DEBUG and pr('>>> Channel._get: %s' % queue)
        q = self._get_queue(queue)
        m = q.read()

        if m:
            q.delete_message(m)
            return deserialize(m.get_body())
        raise Empty()

    def _put(self, queue, message, **kwargs):
        """Put `message` onto `queue`."""
        DEBUG and pr('>>> Channel._put: %s, %s' % (queue, message))
        q = self._get_queue(queue)
        m = q.new_message(serialize(message))
        q.write(m)

    def _purge(self, queue):
        """Remove all messages from `queue`."""
        DEBUG and pr('>>> Channel._purge: %s' % queue)
        return self._get_queue(queue).clear()

    def _size(self, queue):
        """Return the number of messages in `queue` as an :class:`int`."""
        DEBUG and pr('>>> Channel._size: %s' % queue)
        return self._get_queue(queue).count()

    def _delete(self, queue):
        """Delete `queue`.

        This just purges the queue, if you need to do more you can
        override this method.

        """
        DEBUG and pr('>>> Channel._delete: %s' % queue)

        self._purge(queue)
        self._get_queue(queue).delete()
        try:
            del self.queue_cache[queue]
        except KeyError:
            pass
                
    def _new_queue(self, queue, **kwargs):
        """Create new queue.

        Some implementations needs to do additiona actions when
        the queue is created.  You can do so by overriding this
        method.

        """
        DEBUG and pr('>>> Channel._new_queue: %s' % queue)
        return self._get_queue(queue)

    def _has_queue(self, queue, **kwargs):
        """Verify that queue exists.

        Should return :const:`True` if the queue exists or :const:`False`
        otherwise.

        """
        DEBUG and pr('>>> Channel._has_queue: %s' % queue)
        return True
    
    def _get_queue(self, queue):
        # "." is not valid symbol in queue name for SQS. Maybe this should be more pretty.

        #cache to reduce requests number
        if not queue in self.queue_cache:
            if queue.split('.')[0] == EVENT_QUEUE_NAME:
                queue_name = EVENT_QUEUE_NAME
            else:
                queue_name = queue
            queue_name = self.queue_prefix+'.'+queue_name
            
            q = self.client.create_queue(queue_name.replace('.', self.DOT_REPLECEMENT))
            self.queue_cache[queue] = q

        return self.queue_cache[queue]
    
    def _poll(self, cycle, timeout=None):
        """Poll a list of queues for available messages."""
        DEBUG and pr('>>> Channel._poll: %s' % cycle)
        return cycle.get()

    def _create_client(self):
        DEBUG and pr('>>> Channel._create_client')
        access_key = self.connection.client.userid
        secret_key = self.connection.client.password           
        return self.Client(access_key, secret_key)

    @cached_property
    def client(self):
        return self._create_client()

    @client.deleter
    def client(self, client):
        client.connection.disconnect()
        
class Transport(virtual.Transport):
    Channel = Channel

    def __init__(self, *args, **kwargs):
        super(Transport, self).__init__(*args, **kwargs)
        self.connection_errors = (
            boto_exceptions.BotoServerError,
        ) 
        self.channel_errors = (
            boto_exceptions.BotoClientError,
            boto_exceptions.BotoServerError,
        )
            
    def establish_connection(self):
        return self
