"""
Amazon SQS backend for carrot
"""

from carrot.backends.base import BaseMessage, BaseBackend
from boto.sqs.connection import SQSConnection
from boto.sqs.message import MHMessage
from boto.sqs.queue import Queue as SQSQueue
import itertools
import time

class Connection(SQSConnection):

    def drain_events(self, allowed_methods=None, timeout=None):
        pass
  
class Message(BaseMessage):
    
    def __init__(self, backend, sqs_message):
        super(Message, self).__init__(backend)
        print 'Received message'
        self.body = sqs_message.get('data')
        self.content_type = sqs_message.get('content_type')
        self.content_encoding = sqs_message.get('content_encoding')

class Backend(BaseBackend):
    sqs_message_class = MHMessage
    
    def __init__(self, connection, **kwargs):
        self.connection = connection
        #This is ugly hack to get options for Amazon SQS connection 
        #without changing a lot of code
        #I hope fix this in future
        self.access_key = connection.userid
        self.secret_key = connection.password
    
    @property
    def channel(self):
        #fix AttributeError in celery.messaging, line 240
        pass
    
    @property
    def sqs_con(self):
        return self.connection.connection
    
    def queue_declare(self, queue, durable, exclusive, auto_delete, warn_if_exists=False, 
                      arguments=None):
        """Declare a queue by name."""
        #TODO: handle warn_if_exists
        print ">>> queue_declare", queue

        queue_obj = self.sqs_con.create_queue(queue)
        queue_obj.set_message_class(self.sqs_message_class)
        return queue_obj

    def queue_delete(self, *args, **kwargs):
        """Delete a queue by name."""
        print ">>> queue_delete", args, kwargs

    def exchange_declare(self, *args, **kwargs):
        """Declare an exchange by name."""
        print ">>> exchange_declare", args, kwargs

    def queue_bind(self, *args, **kwargs):
        """Bind a queue to an exchange."""
        print ">>> queue_bind", args, kwargs

    def get(self, queue):
        """Pop a message off the queue."""
        print ">>> get", queue
        
        raw_msg = queue.read()
        
        #FIXME: MHM message does not work with Pickle object good. It brokes message
        
        return raw_msg
        
    def declare_consumer(self, queue, no_ack, callback, consumer_tag,
                         nowait=False):
        print ">>> declare_consumer", queue, callback, consumer_tag, nowait
        self.queue = self.sqs_con.get_queue(queue)
        self.queue.set_message_class(self.sqs_message_class)
        self.no_ack = no_ack
        self.callback = callback
        self.consumer_tag = consumer_tag
        self.nowait = nowait
        self.drain_events(self.queue, self.callback)

    def drain_events(self, queue=None, callback=None, timeout=None):
        print ">>> drain_events..."
        queue = queue or self.queue
        callback = callback or self.callback
        message = self.get(queue)
        if message:
            callback(message)
        else:
            time.sleep(0.1)
        
    def consume(self, limit=None):
        """Iterate over the declared consumers."""
        print ">>> consume", limit
        
        for total_message_count in itertools.count():
            if limit and total_message_count >= limit:
                raise StopIteration
            
            self.drain_events()
            yield True

    def cancel(self, *args, **kwargs):
        """Cancel the consumer."""
        print ">>> cancel", args, kwargs

    def ack(self, delivery_tag):
        """Acknowledge the message."""
        print ">>> ack", delivery_tag

    def queue_purge(self, queue, **kwargs):
        """Discard all messages in the queue. This will delete the messages
        and results in an empty queue."""
        print ">>> queue_purge", queue, kwargs
        return 0

    def reject(self, delivery_tag):
        """Reject the message."""
        print ">>> reject", delivery_tag

    def requeue(self, delivery_tag):
        """Requeue the message."""
        print ">>> requeue", delivery_tag

    def purge(self, queue, **kwargs):
        """Discard all messages in the queue."""
        print ">>> purge", queue, kwargs

    def message_to_python(self, raw_message):
        """Convert received message body to a python datastructure."""
        print ">>> message_to_python", raw_message
        #import traceback
        #traceback.print_stack()
        return Message(self, raw_message)

    def prepare_message(self, message_data, delivery_mode, priority=None,
                content_type=None, content_encoding=None):
        """Prepare message for sending."""
        print ">>> prepare_message", message_data,  content_type, content_encoding
        msg = self.sqs_message_class()
        msg['data'] = message_data
        msg['content_type'] = content_type
        msg['content_encoding'] = content_encoding
        return msg

    def publish(self, message, exchange, routing_key, **kwargs):
        """Publish a message."""
        print ">>> publish", message, exchange, routing_key, kwargs
        if self.sqs_con.lookup(routing_key):
            queue = self.sqs_con.get_queue(routing_key)
        else:
            queue = self.sqs_con.create_queue(routing_key)
        queue.write(message)

    def close(self):
        """Close the backend."""
        print ">>> close"

    def establish_connection(self):
        """Establish a connection to the backend."""
        print ">>> establish_connection"
        return Connection(self.access_key, self.secret_key)

    def close_connection(self, connection):
        """Close the connection."""
        print ">>> close_connection", connection

    def flow(self, active):
        """Enable/disable flow from peer."""
        print ">>> flow", active

    def qos(self, prefetch_size, prefetch_count, apply_global=False):
        """Request specific Quality of Service."""
        print ">>> qos", prefetch_size, prefetch_count, apply_global