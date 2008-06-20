#!/usr/bin/python
#shuber, 2008-06-04

__author__ = "shuber"


import gobject
import gtk
import vte

import DbgTerminal
import StatusFrame


class WatchesFrame (StatusFrame.StatusFrame):


	def __init__(self, debugger):

		StatusFrame.StatusFrame.__init__(self, debugger)
		self.set_label("Watches")

		debugger.gotActiveCallback += [self.updateValues]

		vbox = gtk.VBox(False, 5)
		self.add(vbox)

		hbox = gtk.HBox()
		vbox.pack_start(hbox, False, False)
		
		self.addBtn = gtk.Button(stock=gtk.STOCK_ADD)
		self.delBtn = gtk.Button(stock=gtk.STOCK_REMOVE)
		hbox.add(self.addBtn)
		hbox.add(self.delBtn)

		sw = gtk.ScrolledWindow()
		sw.set_shadow_type(gtk.SHADOW_ETCHED_IN)
		sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
		vbox.add(sw)

		self.model = self.__createModel()
		self.tv = gtk.TreeView(self.model)
		self.tv.set_rules_hint(True)
		self.tv.get_selection().set_mode(gtk.SELECTION_MULTIPLE)

		self.__addColumns(self.tv)	
		sw.add(self.tv)

		self.addBtn.connect("clicked", self.addBtnClicked)
		self.delBtn.connect("clicked", self.delBtnClicked)



	def __createModel(self):
	
		model = gtk.ListStore(gobject.TYPE_STRING, gobject.TYPE_STRING, \
				gobject.TYPE_BOOLEAN)

		return model


	def __addColumns(self, tv):

		model = tv.get_model()

		renderer = gtk.CellRendererText()
		renderer.connect("edited", self.onExprEdited, model)
		renderer.set_data("column", 0)
		col = gtk.TreeViewColumn("Expr", renderer, text=0, editable=2)
		col.set_resizable(True)
		tv.append_column(col)


		renderer = gtk.CellRendererText()
		renderer.set_data("column", 1)
		col = gtk.TreeViewColumn("Result", renderer, text=1)
		col.set_resizable(True)
		tv.append_column(col)


	def onExprEdited(self, cell, pathStr, expr, model):
		iter = model.get_iter_from_string(pathStr)
		path = model.get_path(iter)[0]
		col = cell.get_data("column")

		model.set(iter, 0, expr)

		if self.debugger.isActive():
			res = self.debugger.getExpression(expr)
			model.set(iter, 1, res)


	def applyConfiguration(self, conf):
		for w in conf.watches:
			iter = self.model.append()
			self.model.set(iter, 0, w["expr"], 1, "<unkown>", 2, True)
		self.updateValues(None, None)


	def fillConfiguration(self, conf):

		iter = self.model.get_iter_first()
		while iter != None:
			expr, = self.model.get(iter, 0)
			conf.parseWatch(expr)
			iter = self.model.iter_next(iter)


	def addBtnClicked(self, btn):
		iter = self.model.append()
		self.model.set(iter, 0, "0", 1, "0", 2, True)

	def delBtnClicked(self, btn):
		selection = self.tv.get_selection()
		model, paths = selection.get_selected_rows()

		for path in reversed(paths):
			iter = model.get_iter(path)
			model.remove(iter)

	def updateValues(self, status, param):
		iter = self.model.get_iter_first()
		while iter != None:
			expr, = self.model.get(iter, 0)
			res = self.debugger.getExpression(expr)
			self.model.set(iter, 1, res)

			iter = self.model.iter_next(iter)

