import logging
from socketIO_client_nexus import SocketIO, BaseNamespace, LoggingNamespace

class CocoBuyinNamespace(BaseNamespace):
    def on_connect(self):
        print ('coco buyin connected.')
    def on_disconnect(self):
        print ('coco buyin disconnected.')
    def on_reconnect(self):
        print ('coco buyin reconnected.')
    def on_buyinlist(self, data):
        pass

class CocoBuyinTask:
    buyinCallback = None
    url = None
    socketIO = None

    def __init__(self, url):
        self.url = url
    