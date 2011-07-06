# -*- coding: utf-8 -*-

import redis
from django.conf import settings

REDIS_HOST = getattr(settings, 'REDIS_HOST', 'localhost')
REDIS_PORT = getattr(settings, 'REDIS_PORT', 6379)
REDIS_DB = getattr(settings, 'REDIS_DB', 0)

class Client(object):
    def __init__(self, **kwargs):
        self.connection_settings = kwargs or {'host': REDIS_HOST,
                'port': REDIS_PORT, 'db': REDIS_DB}

    def redis(self):
        return redis.Redis(**self.connection_settings)

    def update(self, d):
        self.connection_settings.update(d)

def connection_setup(**kwargs):
    global connection, client
    if client:
        client.update(kwargs)
    else:
        client = Client(**kwargs)
    connection = client.redis()

def get_client():
    global connection
    return connection

client = Client()
connection = client.redis()

__all__ = ['connection_setup', 'get_client']
