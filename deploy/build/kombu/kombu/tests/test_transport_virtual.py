from kombu.tests.utils import unittest

from kombu.connection import BrokerConnection
from kombu.transport import virtual
from kombu.utils import gen_unique_id

from kombu.tests.utils import redirect_stdouts


def client():
    return BrokerConnection(transport="kombu.transport.virtual.Transport")


def memory_client():
    return BrokerConnection(transport="memory")


class test_BrokerState(unittest.TestCase):

    def test_constructor(self):
        s = virtual.BrokerState()
        self.assertTrue(hasattr(s, "exchanges"))
        self.assertTrue(hasattr(s, "bindings"))

        t = virtual.BrokerState(exchanges=16, bindings=32)
        self.assertEqual(t.exchanges, 16)
        self.assertEqual(t.bindings, 32)


class test_QoS(unittest.TestCase):

    def setUp(self):
        self.q = virtual.QoS(client().channel(), prefetch_count=10)

    def tearDown(self):
        self.q._on_collect.cancel()

    def test_constructor(self):
        self.assertTrue(self.q.channel)
        self.assertTrue(self.q.prefetch_count)
        self.assertFalse(self.q._delivered.restored)
        self.assertTrue(self.q._on_collect)

    @redirect_stdouts
    def test_can_consume(self, stdout, stderr):
        _restored = []

        class RestoreChannel(virtual.Channel):
            do_restore = True

            def _restore(self, message):
                _restored.append(message)

        self.assertTrue(self.q.can_consume())
        for i in range(self.q.prefetch_count - 1):
            self.q.append(i, gen_unique_id())
            self.assertTrue(self.q.can_consume())
        self.q.append(i + 1, gen_unique_id())
        self.assertFalse(self.q.can_consume())

        tag1 = self.q._delivered.keys()[0]
        self.q.ack(tag1)
        self.assertTrue(self.q.can_consume())

        tag2 = gen_unique_id()
        self.q.append(i + 2, tag2)
        self.assertFalse(self.q.can_consume())
        self.q.reject(tag2)
        self.assertTrue(self.q.can_consume())

        self.q.channel = RestoreChannel(self.q.channel.connection)
        tag3 = gen_unique_id()
        self.q.append(i + 3, tag3)
        self.q.reject(tag3, requeue=True)
        self.q.restore_unacked_once()
        self.assertListEqual(_restored, [11, 9, 8, 7, 6, 5, 4, 3, 2, 1])
        self.assertTrue(self.q._delivered.restored)
        self.assertFalse(self.q._delivered)

        self.q.restore_unacked_once()
        self.q._delivered.restored = False
        self.q.restore_unacked_once()

        self.assertTrue(stderr.getvalue())
        self.assertFalse(stdout.getvalue())


class test_Message(unittest.TestCase):

    def test_create(self):
        c = client().channel()
        data = c.prepare_message("the quick brown fox...")
        tag = data["properties"]["delivery_tag"] = gen_unique_id()
        message = c.message_to_python(data)
        self.assertIsInstance(message, virtual.Message)
        self.assertIs(message, c.message_to_python(message))

        self.assertEqual(message.body,
                         "the quick brown fox...".encode("utf-8"))
        self.assertTrue(message.delivery_tag, tag)

    def test_serializable(self):
        c = client().channel()
        data = c.prepare_message("the quick brown fox...")
        tag = data["properties"]["delivery_tag"] = gen_unique_id()
        message = c.message_to_python(data)
        dict_ = message.serializable()
        self.assertEqual(dict_["body"],
                         "the quick brown fox...".encode("utf-8"))
        self.assertEqual(dict_["properties"]["delivery_tag"], tag)


class test_AbstractChannel(unittest.TestCase):

    def test_get(self):
        self.assertRaises(NotImplementedError,
                          virtual.AbstractChannel()._get, "queue")

    def test_put(self):
        self.assertRaises(NotImplementedError,
                          virtual.AbstractChannel()._put, "queue", "m")

    def test_size(self):
        self.assertEqual(virtual.AbstractChannel()._size("queue"), 0)

    def test_purge(self):
        self.assertRaises(NotImplementedError,
                          virtual.AbstractChannel()._purge, "queue")

    def test_delete(self):
        self.assertRaises(NotImplementedError,
                          virtual.AbstractChannel()._delete, "queue")

    def test_new_queue(self):
        self.assertIsNone(virtual.AbstractChannel()._new_queue("queue"))

    def test_poll(self):

        class Cycle(object):
            called = False

            def get(self):
                self.called = True
                return True

        cycle = Cycle()
        self.assertTrue(virtual.AbstractChannel()._poll(cycle))
        self.assertTrue(cycle.called)


class test_Channel(unittest.TestCase):

    def setUp(self):
        self.channel = client().channel()

    def tearDown(self):
        if self.channel._qos is not None:
            self.channel._qos._on_collect.cancel()

    def test_exchange_declare(self):
        c = self.channel
        c.exchange_declare("test_exchange_declare", "direct",
                           durable=True, auto_delete=True)
        self.assertIn("test_exchange_declare", c.state.exchanges)
        # can declare again with same values
        c.exchange_declare("test_exchange_declare", "direct",
                           durable=True, auto_delete=True)
        self.assertIn("test_exchange_declare", c.state.exchanges)

        # using different values raises NotEquivalentError
        self.assertRaises(virtual.NotEquivalentError,
            c.exchange_declare, "test_exchange_declare", "direct",
            durable=False, auto_delete=True)

    def test_exchange_delete(self, ex="test_exchange_delete"):
        class PurgeChannel(virtual.Channel):
            purged = []

            def _purge(self, queue):
                self.purged.append(queue)

        c = PurgeChannel(self.channel.connection)

        c.exchange_declare(ex, "direct", durable=True, auto_delete=True)
        self.assertIn(ex, c.state.exchanges)
        self.assertNotIn(ex, c.state.bindings)  # no bindings yet
        c.exchange_delete(ex)
        self.assertNotIn(ex, c.state.exchanges)

        c.exchange_declare(ex, "direct", durable=True, auto_delete=True)
        c.queue_declare(ex)
        c.queue_bind(ex, ex, ex)
        self.assertTrue(c.state.bindings[ex])
        c.exchange_delete(ex)
        self.assertNotIn(ex, c.state.bindings)
        self.assertIn(ex, c.purged)

    def test_queue_delete__if_empty(self, n="test_queue_delete__if_empty"):
        class PurgeChannel(virtual.Channel):
            purged = []
            size = 30

            def _purge(self, queue):
                self.purged.append(queue)

            def _size(self, queue):
                return self.size

        c = PurgeChannel(self.channel.connection)
        c.exchange_declare(n)
        c.queue_declare(n)
        c.queue_bind(n, n, n)
        c.queue_bind(n, n, n)   # tests code path that returns
                                # if queue already bound.

        c.queue_delete(n, if_empty=True)
        self.assertIn(n, c.state.bindings)

        c.size = 0
        c.queue_delete(n, if_empty=True)
        self.assertNotIn(n, c.state.bindings)
        self.assertIn(n, c.purged)

    def test_queue_purge(self, n="test_queue_purge"):

        class PurgeChannel(virtual.Channel):
            purged = []

            def _purge(self, queue):
                self.purged.append(queue)

        c = PurgeChannel(self.channel.connection)
        c.exchange_declare(n)
        c.queue_declare(n)
        c.queue_bind(n, n, n)
        c.queue_purge(n)
        self.assertIn(n, c.purged)

    def test_basic_publish__get__consume__restore(self,
            n="test_basic_publish"):
        c = memory_client().channel()

        c.exchange_declare(n)
        c.queue_declare(n)
        c.queue_bind(n, n, n)
        c.queue_declare(n + "2")
        c.queue_bind(n + "2", n, n)

        m = c.prepare_message("nthex quick brown fox...")
        c.basic_publish(m, n, n)

        r1 = c.message_to_python(c.basic_get(n))
        self.assertTrue(r1)
        self.assertEqual(r1.body,
                         "nthex quick brown fox...".encode("utf-8"))
        self.assertIsNone(c.basic_get(n))

        consumer_tag = gen_unique_id()

        c.basic_consume(n + "2", False, consumer_tag=consumer_tag,
                                        callback=lambda *a: None)
        self.assertIn(n + "2", c._active_queues)
        r2, _ = c.drain_events()
        r2 = c.message_to_python(r2)
        self.assertEqual(r2.body,
                         "nthex quick brown fox...".encode("utf-8"))
        self.assertEqual(r2.delivery_info["exchange"], n)
        self.assertEqual(r2.delivery_info["routing_key"], n)
        self.assertRaises(virtual.Empty, c.drain_events)
        c.basic_cancel(consumer_tag)

        c._restore(r2)
        r3 = c.message_to_python(c.basic_get(n))
        self.assertTrue(r3)
        self.assertEqual(r3.body, "nthex quick brown fox...".encode("utf-8"))
        self.assertIsNone(c.basic_get(n))

    def test_basic_ack(self):

        class MockQoS(virtual.QoS):
            was_acked = False

            def ack(self, delivery_tag):
                self.was_acked = True

        self.channel._qos = MockQoS(self.channel)
        self.channel.basic_ack("foo")
        self.assertTrue(self.channel._qos.was_acked)

    def test_basic_recover__requeue(self):

        class MockQoS(virtual.QoS):
            was_restored = False

            def restore_unacked(self):
                self.was_restored = True

        self.channel._qos = MockQoS(self.channel)
        self.channel.basic_recover(requeue=True)
        self.assertTrue(self.channel._qos.was_restored)

    def test_basic_recover(self):
        self.assertRaises(NotImplementedError,
                          self.channel.basic_recover, requeue=False)

    def test_basic_reject(self):

        class MockQoS(virtual.QoS):
            was_rejected = False

            def reject(self, delivery_tag, requeue=False):
                self.was_rejected = True

        self.channel._qos = MockQoS(self.channel)
        self.channel.basic_reject("foo")
        self.assertTrue(self.channel._qos.was_rejected)

    def test_basic_qos(self):
        self.channel.basic_qos(prefetch_count=128)
        self.assertEqual(self.channel._qos.prefetch_count, 128)

    def test_lookup__undeliverable(self, n="test_lookup__undeliverable"):
        self.assertListEqual(self.channel._lookup(n, n, "ae.undeliver"),
                             ["ae.undeliver"])

    def test_context(self):
        x = self.channel.__enter__()
        self.assertIs(x, self.channel)
        x.__exit__()
        self.assertTrue(x.closed)

    def test_cycle_property(self):
        self.assertTrue(self.channel.cycle)

    def test_flow(self):
        self.assertRaises(NotImplementedError, self.channel.flow, False)


class test_Transport(unittest.TestCase):

    def setUp(self):
        self.transport = client().transport

    def test_close_nonexisting_channel(self):
        self.transport.close_channel("foo")

    def test_close_connection(self):
        c1 = self.transport.create_channel(self.transport)
        c2 = self.transport.create_channel(self.transport)
        self.assertEqual(len(self.transport.channels), 2)
        self.transport.close_connection(self.transport)
        self.assertFalse(self.transport.channels)
        del(c1)  # so pyflakes doesn't complain
        del(c2)

    def test_drain_channel(self):
        channel = self.transport.create_channel(self.transport)
        self.assertRaises(virtual.Empty, self.transport._drain_channel,
                          channel)
