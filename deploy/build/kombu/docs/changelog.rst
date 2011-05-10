================
 Change history
================

1.0.4
=====
:release-date: 2011-02-28 16:00 P.M CET

* Added Transport.polling_interval

    Used by django-kombu to increase the time to sleep between SELECTs when
    there are no messages in the queue.

    Users of django-kombu should upgrade to django-kombu v0.9.2.

1.0.3
=====
:release-date: 2011-02-12 16:00 P.M CET

* ConnectionPool: Re-connect if amqplib connection closed

* Adds ``Queue.as_dict`` + ``Exchange.as_dict``.

* Copyright headers updated to include 2011.

1.0.2
=====
:release-date: 2011-01-31 10:45 P.M CET

* amqplib: Message properties were not set properly.
* Ghettoq backend names are now automatically translated to the new names.

1.0.1
=====
:release-date: 2011-01-28 12:00 P.M CET

* Redis: Now works with Linux (epoll)

1.0.0
=====
:release-date: 2011-01-27 12:00 P.M CET

* Initial release

0.1.0
=====
:release-date: 2010-07-22 4:20 P.M CET

* Initial fork of carrot
