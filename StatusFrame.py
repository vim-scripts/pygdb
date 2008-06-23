#!/usr/bin/python
#shuber, 2008-06-09

__author__ = "shuber"


import gtk


class StatusFrame (gtk.Frame):

	def __init__(self, debugger):
		gtk.Frame.__init__(self)
		self.debugger = debugger

	def applyConfiguration(self, conf):
		raise NotImplemented()

	def fillConfiguration(self, conf):
		raise NotImplemented()

	def updateValues(self, status, param):
		raise NotImplemented()



