"""
kombu.transport.virtual
=======================

Virtual transport implementation.

Emulates the AMQ API for non-AMQ transports.

:copyright: (c) 2009, 2011 by Ask Solem.
:license: BSD, see LICENSE for more details.

"""
import socket

from itertools import count
from time import sleep, time
from Queue import Empty

from kombu.exceptions import StdChannelError
from kombu.transport import base
from kombu.utils import emergency_dump_state, say
from kombu.utils.compat import OrderedDict
from kombu.utils.finalize import Finalize

from kombu.transport.virtual.scheduling import FairCycle
from kombu.transport.virtual.exchange import STANDARD_EXCHANGE_TYPES


class NotEquivalentError(Exception):
    """Entity declaration is not equivalent to the previous declaration."""
    pass


class BrokerState(object):

    #: exchange declarations.
    exchanges = None

    #: active bindings.
    bindings = None

    def __init__(self, exchanges=None, bindings=None):
        if exchanges is None:
            exchanges = {}
        if bindings is None:
            bindings = {}
        self.exchanges = exchanges
        self.bindings = bindings


class QoS(object):
    """Quality of Service guarantees.

    Only supports `prefetch_count` at this point.

    :param channel: AMQ Channel.
    :keyword prefetch_count: Initial prefetch count (defaults to 0).

    """

    #: current prefetch count value
    prefetch_count = 0

    #: :class:`~collections.OrderedDict` of active messages.
    _delivered = None

    def __init__(self, channel, prefetch_count=0):
        self.channel = channel
        self.prefetch_count = prefetch_count or 0

        self._delivered = OrderedDict()
        self._delivered.restored = False
        self._on_collect = Finalize(self,
                                    self.restore_unacked_once,
                                    exitpriority=1)

    def can_consume(self):
        """Returns true if the channel can be consumed from.

        Used to ensure the client adhers to currently active
        prefetch limits.

        """
        pcount = self.prefetch_count
        return (not pcount or len(self._delivered) < pcount)

    def append(self, message, delivery_tag):
        """Append message to transactional state."""
        self._delivered[delivery_tag] = message

    def ack(self, delivery_tag):
        """Acknowledge message and remove from transactional state."""
        self._delivered.pop(delivery_tag, None)

    def reject(self, delivery_tag, requeue=False):
        """Remove from transactional state and requeue message."""
        message = self._delivered.pop(delivery_tag)
        if requeue:
            self.channel._restore(message)

    def restore_unacked(self):
        """Restore all unacknowledged messages."""
        delivered = self._delivered
        errors = []

        while delivered:
            try:
                _, message = delivered.popitem()
            except KeyError:  # pragma: no cover
                break

            try:
                self.channel._restore(message)
            except (KeyboardInterrupt, SystemExit, Exception), exc:
                errors.append((exc, message))
        delivered.clear()
        return errors

    def restore_unacked_once(self):
        """Restores all uncknowledged message at shutdown/gc collect.

        Will only be done once for each instance.

        """
        state = self._delivered

        if not self.channel.do_restore or getattr(state, "restored"):
            assert not state
            return

        try:
            if state:
                say("Restoring unacknowledged messages: %s", state)
                unrestored = self.restore_unacked()

                if unrestored:
                    errors, messages = zip(*unrestored)
                    say("UNABLE TO RESTORE %s MESSAGES: %s",
                            len(errors), errors)
                    emergency_dump_state(messages)
        finally:
            state.restored = True


class Message(base.Message):

    def __init__(self, channel, payload, **kwargs):
        properties = payload["properties"]
        fields = {"body": payload.get("body"),
                  "delivery_tag": properties["delivery_tag"],
                  "content_type": payload.get("content-type"),
                  "content_encoding": payload.get("content-encoding"),
                  "headers": payload.get("headers"),
                  "properties": properties,
                  "delivery_info": properties.get("delivery_info"),
                  "postencode": "utf-8"}
        super(Message, self).__init__(channel, **dict(kwargs, **fields))

    def serializable(self):
        return {"body": self.body,
                "properties": self.properties,
                "content-type": self.content_type,
                "content-encoding": self.content_encoding,
                "headers": self.headers}


class AbstractChannel(object):
    """This is an abstract class defining the channel methods
    you'd usually want to implement in a virtual channel.

    Do not subclass directly, but rather inherit from :class:`Channel`
    instead.

    """

    def _get(self, queue, timeout=None):
        """Get next message from `queue`."""
        raise NotImplementedError("Virtual channels must implement _get")

    def _put(self, queue, message):
        """Put `message` onto `queue`."""
        raise NotImplementedError("Virtual channels must implement _put")

    def _purge(self, queue):
        """Remove all messages from `queue`."""
        raise NotImplementedError("Virtual channels must implement _purge")

    def _size(self, queue):
        """Return the number of messages in `queue` as an :class:`int`."""
        return 0

    def _delete(self, queue):
        """Delete `queue`.

        This just purges the queue, if you need to do more you can
        override this method.

        """
        self._purge(queue)

    def _new_queue(self, queue, **kwargs):
        """Create new queue.

        Some implementations needs to do additiona actions when
        the queue is created.  You can do so by overriding this
        method.

        """
        pass

    def _has_queue(self, queue, **kwargs):
        """Verify that queue exists.

        Should return :const:`True` if the queue exists or :const:`False`
        otherwise.

        """
        return True

    def _poll(self, cycle, timeout=None):
        """Poll a list of queues for available messages."""
        return cycle.get()


class Channel(AbstractChannel):
    """Virtual channel.

    :param connection: The transport instance this channel is part of.

    """
    #: message class used.
    Message = Message

    #: flag to restore unacked messages when channel
    #: goes out of scope.
    do_restore = True

    #: mapping of exchange types and corresponding classes.
    exchange_types = dict(STANDARD_EXCHANGE_TYPES)

    #: flag set if the channel supports fanout exchanges.
    supports_fanout = False

    #: counter used to generate delivery tags for this channel.
    _next_delivery_tag = count(1).next

    def __init__(self, connection, **kwargs):
        self.connection = connection
        self._consumers = set()
        self._cycle = None
        self._tag_to_queue = {}
        self._active_queues = []
        self._qos = None
        self.closed = False

        # instantiate exchange types
        self.exchange_types = dict((typ, cls(self))
                    for typ, cls in self.exchange_types.items())

    def exchange_declare(self, exchange, type="direct", durable=False,
            auto_delete=False, arguments=None, nowait=False):
        """Declare exchange."""
        try:
            prev = self.state.exchanges[exchange]
            if not self.typeof(exchange).equivalent(prev, exchange, type,
                                                    durable, auto_delete,
                                                    arguments):
                raise NotEquivalentError(
                        "Cannot redeclare exchange %r in vhost %r with "
                        "different type, durable or autodelete value" % (
                            exchange,
                            self.connection.client.virtual_host or "/"))
        except KeyError:
            self.state.exchanges[exchange] = {
                    "type": type,
                    "durable": durable,
                    "auto_delete": auto_delete,
                    "arguments": arguments or {},
                    "table": [],
            }

    def exchange_delete(self, exchange, if_unused=False, nowait=False):
        """Delete `exchange` and all its bindings."""
        for rkey, _, queue in self.get_table(exchange):
            self.queue_delete(queue, if_unused=True, if_empty=True)
        self.state.exchanges.pop(exchange, None)

    def queue_declare(self, queue, passive=False, **kwargs):
        """Declare queue."""
        if passive and not self._has_queue(queue, **kwargs):
            raise StdChannelError("404",
                    u"NOT_FOUND - no queue %r in vhost %r" % (
                        queue, self.connection.client.virtual_host or '/'),
                    (50, 10), "Channel.queue_declare")
        else:
            self._new_queue(queue, **kwargs)
        return queue, self._size(queue), 0

    def queue_delete(self, queue, if_unusued=False, if_empty=False, **kwargs):
        """Delete queue."""
        if if_empty and self._size(queue):
            return
        exchange, routing_key = self.state.bindings[queue]
        self._delete(queue)
        self.state.bindings.pop(queue, None)

    def queue_bind(self, queue, exchange, routing_key, arguments=None,
            **kwargs):
        """Bind `queue` to `exchange` with `routing key`."""
        if queue in self.state.bindings:
            return
        table = self.state.exchanges[exchange].setdefault("table", [])
        self.state.bindings[queue] = exchange, routing_key
        meta = self.typeof(exchange).prepare_bind(queue,
                                                  exchange,
                                                  routing_key,
                                                  arguments)
        table.append(meta)
        if self.supports_fanout:
            self._queue_bind(exchange, *meta)

    def queue_purge(self, queue, **kwargs):
        """Remove all ready messages from queue."""
        return self._purge(queue)

    def basic_publish(self, message, exchange, routing_key, **kwargs):
        """Publish message."""
        message["properties"]["delivery_info"]["exchange"] = exchange
        message["properties"]["delivery_info"]["routing_key"] = routing_key
        message["properties"]["delivery_tag"] = self._next_delivery_tag()
        if self.typeof(exchange).type == "fanout" and self.supports_fanout:
            self._put_fanout(exchange, message, **kwargs)
        else:
            for queue in self._lookup(exchange, routing_key):
                self._put(queue, message, **kwargs)

    def basic_consume(self, queue, no_ack, callback, consumer_tag, **kwargs):
        """Consume from `queue`"""
        self._tag_to_queue[consumer_tag] = queue
        self._active_queues.append(queue)

        def _callback(raw_message):
            message = self.Message(self, raw_message)
            if not no_ack:
                self.qos.append(message, message.delivery_tag)
            return callback(message)

        self.connection._callbacks[queue] = _callback
        self._consumers.add(consumer_tag)

        self._reset_cycle()

    def basic_cancel(self, consumer_tag):
        """Cancel consumer by consumer tag."""
        if consumer_tag in self._consumers:
            self._consumers.remove(consumer_tag)
            self._reset_cycle()
            queue = self._tag_to_queue.pop(consumer_tag, None)
            try:
                self._active_queues.remove(queue)
            except ValueError:
                pass
            self.connection._callbacks.pop(queue, None)

    def basic_get(self, queue, **kwargs):
        """Get message by direct access (synchronous)."""
        try:
            return self._get(queue)
        except Empty:
            pass

    def basic_ack(self, delivery_tag):
        """Acknowledge message."""
        self.qos.ack(delivery_tag)

    def basic_recover(self, requeue=False):
        """Recover unacked messages."""
        if requeue:
            return self.qos.restore_unacked()
        raise NotImplementedError("Does not support recover(requeue=False)")

    def basic_reject(self, delivery_tag, requeue=False):
        """Reject message."""
        self.qos.reject(delivery_tag, requeue=requeue)

    def basic_qos(self, prefetch_size=0, prefetch_count=0,
            apply_global=False):
        """Change QoS settings for this channel.

        Only `prefetch_count` is supported.

        """
        self.qos.prefetch_count = prefetch_count

    def get_table(self, exchange):
        """Get table of bindings for `exchange`."""
        return self.state.exchanges[exchange]["table"]

    def typeof(self, exchange):
        """Get the exchange type instance for `exchange`."""
        type = self.state.exchanges[exchange]["type"]
        return self.exchange_types[type]

    def _lookup(self, exchange, routing_key, default="ae.undeliver"):
        """Find all queues matching `routing_key` for the given `exchange`.

        Returns `default` if no queues matched.

        """
        try:
            table = self.get_table(exchange)
            return self.typeof(exchange).lookup(table, exchange,
                                                routing_key, default)
        except KeyError:
            self._new_queue(default)
            return [default]

    def _restore(self, message):
        """Redeliver message to its original destination."""
        delivery_info = message.delivery_info
        message = message.serializable()
        message["redelivered"] = True
        for queue in self._lookup(delivery_info["exchange"],
                                  delivery_info["routing_key"]):
            self._put(queue, message)

    def drain_events(self, timeout=None):
        if self._consumers and self.qos.can_consume():
            if hasattr(self, "_get_many"):
                return self._get_many(self._active_queues, timeout=timeout)
            return self._poll(self.cycle, timeout=timeout)
        raise Empty()

    def message_to_python(self, raw_message):
        """Convert raw message to :class:`Message` instance."""
        if not isinstance(raw_message, self.Message):
            return self.Message(self, payload=raw_message)
        return raw_message

    def prepare_message(self, message_data, priority=None,
            content_type=None, content_encoding=None, headers=None,
            properties=None):
        """Prepare message data."""
        properties = properties or {}
        info = properties.setdefault("delivery_info", {})
        info["priority"] = priority or 0

        return {"body": message_data,
                "content-encoding": content_encoding,
                "content-type": content_type,
                "headers": headers or {},
                "properties": properties or {}}

    def flow(self, active=True):
        """Enable/disable message flow.

        :raises NotImplementedError: as flow
            is not implemented by the base virtual implementation.

        """
        raise NotImplementedError("virtual channels does not support flow.")

    def close(self):
        """Close channel, cancel all consumers, and requeue unacked
        messages."""
        self.closed = True
        for consumer in list(self._consumers):
            self.basic_cancel(consumer)
        self.qos.restore_unacked_once()
        self.connection.close_channel(self)
        if self._cycle is not None:
            self._cycle.close()
            self._cycle = None

    def _reset_cycle(self):
        self._cycle = FairCycle(self._get, self._active_queues, Empty)

    def __enter__(self):
        return self

    def __exit__(self, *exc_info):
        self.close()

    @property
    def state(self):
        """Broker state containing exchanges and bindings."""
        return self.connection.state

    @property
    def qos(self):
        """:class:`QoS` manager for this channel."""
        if self._qos is None:
            self._qos = QoS(self)
        return self._qos

    @property
    def cycle(self):
        if self._cycle is None:
            self._reset_cycle()
        return self._cycle


class Transport(base.Transport):
    """Virtual transport.

    :param client: :class:`~kombu.connection.BrokerConnection` instance

    """
    #: channel class used.
    Channel = Channel

    #: cycle class used.
    Cycle = FairCycle

    #: :class:`BrokerState` containing declared exchanges and
    #: bindings (set by constructor).
    state = BrokerState()

    #: :class:`~kombu.transport.virtual.scheduling.FairCycle` instance
    #: used to fairly drain events from channels (set by constructor).
    cycle = None

    #: default interval between polling channels for new events.
    interval = 1

    #: port number used when no port is specified.
    default_port = None

    #: active channels.
    channels = None

    #: queue/callback map.
    _callbacks = None

    #: Time to sleep between unsuccessful polls.
    polling_interval = 0.1

    def __init__(self, client, **kwargs):
        self.client = client
        self.channels = []
        self._callbacks = {}
        self.cycle = self.Cycle(self._drain_channel, self.channels, Empty)

    def create_channel(self, connection):
        channel = self.Channel(connection)
        self.channels.append(channel)
        return channel

    def close_channel(self, channel):
        try:
            self.channels.remove(channel)
        except ValueError:
            pass

    def establish_connection(self):
        return self     # for drain events

    def close_connection(self, connection):
        self.cycle.close()
        while self.channels:
            try:
                channel = self.channels.pop()
            except KeyError:    # pragma: no cover
                pass
            else:
                channel.close()

    def drain_events(self, connection, timeout=None):
        loop = 0
        time_start = time()
        while 1:
            try:
                item, channel = self.cycle.get(timeout=timeout)
            except Empty:
                if timeout and time() - time_start >= timeout:
                    raise socket.timeout()
                loop += 1
                sleep(self.polling_interval)
            else:
                break

        message, queue = item

        if not queue or queue not in self._callbacks:
            raise KeyError(
                "Received message for queue '%s' without consumers: %s" % (
                    queue, message))

        self._callbacks[queue](message)

    def _drain_channel(self, channel, timeout=None):
        return channel.drain_events(timeout=timeout)
