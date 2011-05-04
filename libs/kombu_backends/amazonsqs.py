from kombu.transport import virtual
from boto.sqs.connection import SQSConnection

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

import logging

class LoggingConnection(SQSConnection):
    
    def _log(self, method_name):
        logging.debug(u'SQSConnection.%s' % method_name)
        
    def create_queue(self, *args, **kwargs):
        self._log(u'create_queue')
        return super(LoggingConnection, self).create_queue(*args, **kwargs)

    def delete_queue(self, *args, **kwargs):
        self._log(u'delete_queue')
        return super(LoggingConnection, self).delete_queue(*args, **kwargs)

    def get_queue_attributes(self, *args, **kwargs):
        self._log(u'get_queue_attributes')
        return super(LoggingConnection, self).get_queue_attributes(*args, **kwargs)

    def set_queue_attribute(self, *args, **kwargs):
        self._log(u'set_queue_attribute')
        return super(LoggingConnection, self).set_queue_attribute(*args, **kwargs)

    def receive_message(self, *args, **kwargs):
        self._log(u'receive_message')
        return super(LoggingConnection, self).receive_message(*args, **kwargs)

    def delete_message(self, *args, **kwargs):
        self._log(u'delete_message')
        return super(LoggingConnection, self).delete_message(*args, **kwargs)

    def delete_message_from_handle(self, *args, **kwargs):
        self._log(u'delete_message_from_handle')
        return super(LoggingConnection, self).delete_message_from_handle(*args, **kwargs)

    def send_message(self, *args, **kwargs):
        self._log(u'send_message')
        return super(LoggingConnection, self).send_message(*args, **kwargs)

    def change_message_visibility(self, *args, **kwargs):
        self._log(u'change_message_visibility')
        return super(LoggingConnection, self).change_message_visibility(*args, **kwargs)

    def get_all_queues(self, *args, **kwargs):
        self._log(u'get_all_queues')
        return super(LoggingConnection, self).get_all_queues(*args, **kwargs)

    def get_queue(self, *args, **kwargs):
        self._log(u'get_queue')
        return super(LoggingConnection, self).get_queue(*args, **kwargs)

    def add_permission(self, *args, **kwargs):
        self._log(u'add_permission')
        return super(LoggingConnection, self).add_permission(*args, **kwargs)

    def remove_permission(self, *args, **kwargs):
        self._log(u'remove_permission')
        return super(LoggingConnection, self).remove_permission(*args, **kwargs)

class Channel(virtual.Channel):
    Client = SQSConnection
    
    DOT_REPLECEMENT = '___'
    supports_fanout = False

    def __init__(self, connection, **kwargs):
        self.queue_prefix = connection.client.virtual_host or ''
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
        if queue.split('.')[0] == EVENT_QUEUE_NAME:
            queue = EVENT_QUEUE_NAME
        queue = self.queue_prefix+'.'+queue
        q = self.client.create_queue(queue.replace('.', self.DOT_REPLECEMENT))
        return q
    
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
    
    def establish_connection(self):
        return self
