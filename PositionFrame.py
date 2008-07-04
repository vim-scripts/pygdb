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


	def __init__(self, debugger, statuswnd):

		StatusFrame.StatusFrame.__init__(self, debugger)
		self.set_label("Position")

		self.statuswnd = statuswnd
		debugger.gotActiveCallback += [self.updateValues]
		debugger.gotInactiveCallback += [self.updateValues]

		self.file = None
		self.bt = None
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

		self.model = self.__createModel()
		self.tv = gtk.TreeView(self.model)
		self.tv.set_rules_hint(True)
		self.tv.get_selection().set_mode(gtk.SELECTION_MULTIPLE)
		self.tv.connect("row-activated", self.rowactivated)

		self.__addColumns(self.tv)
		sw.add(self.tv)

		self.openBtn.connect("clicked", self.openBtnClicked)


	def __createModel(self):	
		model = gtk.ListStore(gobject.TYPE_STRING, gobject.TYPE_STRING, \
				gobject.TYPE_STRING, gobject.TYPE_STRING)

		return model


	def __addColumns(self, tv):

		model = tv.get_model()

		renderer = gtk.CellRendererText()
		renderer.set_data("column", 0)
		col = gtk.TreeViewColumn("Addr", renderer, text=0)
		col.set_resizable(True)
		tv.append_column(col)

		renderer = gtk.CellRendererText()
		renderer.set_data("column", 1)
		col = gtk.TreeViewColumn("Func", renderer, text=1)
		col.set_resizable(True)
		tv.append_column(col)

		renderer = gtk.CellRendererText()
		renderer.set_data("column", 2)
		col = gtk.TreeViewColumn("File", renderer, text=2)
		col.set_resizable(True)
		tv.append_column(col)

		renderer = gtk.CellRendererText()
		renderer.set_data("column", 3)
		col = gtk.TreeViewColumn("Lin", renderer, text=3)
		col.set_resizable(True)
		tv.append_column(col)


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


	def rowactivated(self, tv, path, col, *w):
		no, = path
		no = int(no)
		entry = self.bt[no]
		self.statuswnd.gotoVim(entry[2], entry[3])

	

	def updateValues(self, status, param):
		

		#Remove them all
		iter = self.model.get_iter_first()
		while iter != None:
			newiter = self.model.iter_next(iter)
			self.model.remove(iter)
			iter = newiter


		if status == "break":

	
			#Set current file position
			self.file, self.lineno = param
			self.positionLabel.set_label("%s:%d" % (self.file, self.lineno))

			#Add the entries
			self.bt = self.debugger.getBacktrace()
			for [addr, func, file, lineno] in self.bt:
				iter = self.model.append()

				if addr!=None:
					self.model.set(iter, 0, addr)	

				self.model.set(iter, 1, func)
				self.model.set(iter, 2, file)
				self.model.set(iter, 3, lineno)



		else:
			self.file, self.lineno = None, None
			self.bt = None
			code = ""

			if status == "exited":
				self.positionLabel.set_label("Exited with code %d." % param)
			elif status == "started":
				self.positionLabel.set_label("Started.")
			elif status == "continued":
				self.positionLabel.set_label("Continued.")
			else:
				self.positionLabel.set_label(status)

	
		

	def applyConfiguration(self, conf):
		pass

	def fillConfiguration(self, conf):
		conf.setCurrpos(self.file, self.lineno)

