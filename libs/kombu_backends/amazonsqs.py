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

class Channel(virtual.Channel):
    Client = SQSConnection
    
    def __init__(self, *args, **kwargs):
        super(Channel, self).__init__(*args, **kwargs)
    
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
        q = self.client.create_queue(queue.replace('.', '_'))
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
