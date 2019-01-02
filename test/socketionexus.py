#!/usr/bin/python
# -*- coding: UTF-8 -*-

import traceback
import logging
# pip install socketIO-client
# pip install socketIO-client-2
# from socketIO_client import SocketIO, BaseNamespace, LoggingNamespace
# pip install socketIO-client-nexus
from socketIO_client_nexus import SocketIO, BaseNamespace, LoggingNamespace

# from socketIO_client socketIO_client_nexus

logging.getLogger('socketIO-client-nexus').setLevel(logging.DEBUG)
logging.basicConfig()
cmd_namespace = None

class CMSNamespace(BaseNamespace):
    def on_connect(self, *data):
        print ('------------------------------------------------namespace conneced', data)
    def on_disconnect(self):
        print ('------------------------------------------------namespace disconnected')
    def on_reconnect(self):
        print ('------------------------------------------------namespace reconnected')
    def on_buyindata(self, data):
        print ('------------------------------------------------namespace buyindata:', data)


def on_connect(*data):
    print('++++++++++++++++++++++++++++++++++++++++++++++++++++connected:', data)
def on_disconnect(*data):
    print('++++++++++++++++++++++++++++++++++++++++++++++++++++disconnected:', data)
def on_reconnect(*data):
    print('++++++++++++++++++++++++++++++++++++++++++++++++++++reconnected:', data)

print ('whill init.')
with SocketIO(
        'https://www.cmsweb.club:8000',
        cookies = {
            'connect.sid': 's%3A8672223f-7d72-4ac1-9fa6-3c75e52b74a3.CWJPAHikxMYAmrVl3IKJTXAoIFg5uUH2bwdTzXEhSbQ'
        }
    ) as socketIO:
    print ('init socket io.')
    socketIO.on('connect', on_connect)
    socketIO.on('disconnect', on_disconnect)
    socketIO.on('reconnect', on_reconnect) 

    cms_namespace = socketIO.define(CMSNamespace, '/cms')
    cms_namespace.on('success', lambda id: cms_namespace.on('client:%s' % id, cms_namespace.on_buyindata))
    cms_namespace.emit('authentication')

    print ('already binded.')
    socketIO.wait()
    # while True:
    #     try:
    #         # socketIO.wait(seconds=5)
    #     except:
    #         traceback.print_exc()
