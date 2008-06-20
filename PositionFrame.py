#!/usr/bin/python
#shuber, 2008-06-04

__author__ = "shuber"


import gobject
import gtk
import re
import os
import string
import vte

import DbgTerminal
import StatusFrame


class PositionFrame (StatusFrame.StatusFrame):


	def __init__(self, debugger):

		StatusFrame.StatusFrame.__init__(self, debugger)
		self.set_label("Position")

		debugger.gotActiveCallback += [self.updateValues]
		debugger.gotInactiveCallback += [self.updateValues]

		self.file = None
		self.lineno = 0

		vbox = gtk.VBox(False, 5)
		self.add(vbox)

		hbox = gtk.HBox(False, 10)
		vbox.pack_start(hbox, False, False)
		self.openBtn = gtk.Button(":e")
		hbox.pack_start(self.openBtn, False, False)
		self.positionLabel = gtk.Label()
		hbox.pack_start(self.positionLabel, False, False)

		sw = gtk.ScrolledWindow()
		sw.set_shadow_type(gtk.SHADOW_ETCHED_IN)
		sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
		vbox.add(sw)

		self.srcview = gtk.TextView()
		sw.add(self.srcview)

		self.openBtn.connect("clicked", self.openBtnClicked)


	def openBtnClicked(self, btn):

		if not self.debugger.isActive():
			return
		
		if self.file!=None:
			try:
				cmd = 'gvim --servername pygdb -c ":GDBLoadConfig" %s' % (self.file)
				os.system(cmd)
			except OSError:
				dialog = gtk.MessageDialog(None, \
				gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT, \
				gtk.MESSAGE_ERROR, gtk.BUTTONS_OK, \
				"Error calling editor with '%s'." % cmd) 
				dialog.run()
				dialog.destroy()


	def updateValues(self, status, param):
		
		#Create new text buffer for source view
		buf = gtk.TextBuffer()

		if status == "break":		
			self.file, self.lineno = param
			self.positionLabel.set_label("%s:%d" % (self.file, self.lineno))

			#Get some code
			code = string.join(self.debugger.getBacktrace(), "\n")
			buf.set_text(code)


		else:
			self.file, self.lineno = None, None
			code = ""

			if status == "exited":
				self.positionLabel.set_label("Exited with code %d." % param)
			elif status == "started":
				self.positionLabel.set_label("Started.")
			elif status == "continued":
				self.positionLabel.set_label("Continued.")
			else:
				self.positionLabel.set_label(status)

	
		#Set the buffer
		self.srcview.set_buffer(buf)


		

	def applyConfiguration(self, conf):
		pass

	def fillConfiguration(self, conf):
		conf.setCurrpos(self.file, self.lineno)

