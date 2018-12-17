#!/usr/bin/python
#-- coding: utf-8 --


import threading
import time
from providers import ProviderFactory

class Task(object):

	def __init__(self, interval):
		self.interval = interval
		self.e = threading.Event()
		self.t = threading.Thread(target=self.handle)
		self.api = None

	def setApi(self, conf):
		self.api = ProviderFactory.createProvider(conf[self.providerName], conf['db'])
		self.config = conf
		return self

	def handle(self):
	    while not self.e.wait(self.interval):
			print time.strftime("%Y-%m-%d %H:%M:%S")
			self.callback()

	def start(self):
		self.t.start()

	def cancel(self):
		self.e.set()

	def callback(self):
		pass
