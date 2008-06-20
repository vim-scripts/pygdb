#!/usr/bin/python
#shuber, 2008-06-04

__author__ = "shuber"


import gobject
import gtk
import re
import string
import vte

import DbgTerminal
import StatusFrame


class BreakpointsFrame (StatusFrame.StatusFrame):


	def __init__(self, debugger):

		StatusFrame.StatusFrame.__init__(self, debugger)
		self.set_label("Breakpoints")

		debugger.gotActiveCallback += [self.updateValues]

		vbox = gtk.VBox(False, 5)
		self.add(vbox)

		hbox = gtk.HBox()
		vbox.pack_start(hbox, False, False)
		self.bpEntry = gtk.Entry()
		hbox.add(self.bpEntry)


		hbox = gtk.HBox()
		vbox.pack_start(hbox, False, False)
		self.addBtn = gtk.Button(stock=gtk.STOCK_ADD)
		self.delBtn = gtk.Button(stock=gtk.STOCK_REMOVE)
		self.updBtn = gtk.Button("Update")
		hbox.add(self.addBtn)
		hbox.add(self.delBtn)
		hbox.add(self.updBtn)

		sw = gtk.ScrolledWindow()
		sw.set_shadow_type(gtk.SHADOW_ETCHED_IN)
		sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
		vbox.add(sw)

		self.model = self.__createModel()
		self.tv = gtk.TreeView(self.model)
		self.tv.set_rules_hint(True)
		self.tv.get_selection().set_mode(gtk.SELECTION_MULTIPLE)
		self.tv.get_selection().connect("changed", self.selChanged)

		self.__addColumns(self.tv)	
		sw.add(self.tv)

		self.addBtn.connect("clicked", self.addBtnClicked)
		self.delBtn.connect("clicked", self.delBtnClicked)
		self.updBtn.connect("clicked", self.updBtnClicked)



	def __createModel(self):	
		#Breakpoint number, position and a boolean flag indicating whether BP has been set
		#at debugger yet
		model = gtk.ListStore(gobject.TYPE_STRING, gobject.TYPE_STRING)

		return model


	def __addColumns(self, tv):

		model = tv.get_model()

		renderer = gtk.CellRendererText()
		renderer.set_data("column", 0)
		col = gtk.TreeViewColumn("No", renderer, text=0)
		col.set_resizable(True)
		tv.append_column(col)


		renderer = gtk.CellRendererText()
		renderer.set_data("column", 1)
		col = gtk.TreeViewColumn("Specification", renderer, text=1)
		col.set_resizable(True)
		tv.append_column(col)


	def selChanged(self, sel):
		model, paths = sel.get_selected_rows()

		if len(paths) > 0:
			path = paths[0]
			iter = model.get_iter(path)
			bpspec, = model.get(iter, 1)
			self.bpEntry.set_text(bpspec)



	def addBreakpoint(self, file, lineno, cond=None):

		no = self.debugger.setBreakpoint(file, lineno, cond)
		if no!=None:
			self.addBreakpointToList(no, file, lineno, cond)
		else:
			dialog = gtk.MessageDialog(None, \
				gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT, \
				gtk.MESSAGE_ERROR, gtk.BUTTONS_OK, \
				"Invalid specification!") 
			dialog.run()
			dialog.destroy()


	def applyConfiguration(self, conf):
		for b in conf.breakpoints:
			self.addBreakpoint(b["file"], b["lineno"], b["cond"])
		self.updateValues(None, None)

	def fillConfiguration(self, conf):
		iter = self.model.get_iter_first()
		while iter != None:
			spec, = self.model.get(iter, 1)

			#Replacing file by absolute path
			file = string.split(spec, ":")[0]
			file = self.debugger.toAbsPath(file)
			postfile = string.join( string.split(spec,":")[1:], ":")

			conf.parseBreak(file + ":" + postfile )
			iter = self.model.iter_next(iter)



	def addBreakpointToList(self, no, file, lineno, cond=None):

		if cond==None:
			expr =  "%s:%s" % (str(file), str(lineno))
		else:
			expr = "%s:%s if %s" % (str(file), str(lineno), str(cond))

		iter = self.model.get_iter_first()
		while iter != None:
			newiter = self.model.iter_next(iter)
			#Found a expression which is the same --> remove the breakpoint
			if (expr,) == self.model.get(iter,1):
				self.debugger.delBreakpoint(no)
				return
			iter = newiter
	
		#Add the entry to the breakpoint list
		iter = self.model.append()
		self.model.set(iter, 0, no)	
		self.model.set(iter, 1, expr)


	def addBtnClicked(self, btn):

		if not self.debugger.isActive():
			return


		bpspec = self.bpEntry.get_text()
		bpspec = bpspec.strip()
		rx = re.compile("^[\w/\._\-]+:\d+(\s+if\s+\S+.*)?$")

		#Check if format is correct
		if not rx.search(bpspec):
			dialog = gtk.MessageDialog(None, \
				gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT, \
				gtk.MESSAGE_ERROR, gtk.BUTTONS_OK, \
				"Invalid format!") 
			dialog.run()
			dialog.destroy()
			return


		ifsplit = string.split(bpspec, " if ")

		if len(ifsplit)>1:
			cond = ifsplit[1].strip()
		else:
			cond = None

		pos = ifsplit[0].strip()	
		[file,lineno] = string.split(pos, ":")

		self.addBreakpoint(file, lineno, cond)




	def delBtnClicked(self, btn):

		if not self.debugger.isActive():
			return

		selection = self.tv.get_selection()
		model, paths = selection.get_selected_rows()

		for path in reversed(paths):
			iter = model.get_iter(path)
			bpno, = self.model.get(iter, 0)
			self.debugger.delBreakpoint(bpno)
			model.remove(iter)


	def updBtnClicked(self, btn):

		if not self.debugger.isActive():
			return

		self.updateValues(None, None)


	def updateValues(self, status, param):
		
		bpnts = self.debugger.getBreakpoints()

		#Remove them all
		iter = self.model.get_iter_first()
		while iter != None:
			newiter = self.model.iter_next(iter)
			self.model.remove(iter)
			iter = newiter

		for bp in bpnts:
			[no, file, lineno, cond] = bp
			self.addBreakpointToList(no, file, lineno, cond)


	
