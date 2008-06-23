#!/usr/bin/python
#shuber, 2008-06-04

__author__ = "shuber"


import gtk
import re
import string
import os
import vte

import Configuration
import DbgTerminal
import BreakpointsFrame
import PositionFrame
import WatchesFrame



class StatusWindow (gtk.Window):

	def __init__(self, debugger, vimservername):
		gtk.Window.__init__(self)

		self.vimservername = vimservername
		self.debugger = debugger
		self.debugger.gotActiveCallback += [self.updateValues]
		
		self.set_border_width(5)
		self.set_title("Status")
		self.set_default_size(400,600)
		self.connect("destroy", DbgTerminal.quitHandler)


		#Vbox container of frames
		vbox = gtk.VBox(False, 5)
		self.add(vbox)

	
		#Adding the frames
		self.frames = []
		self.frames += [PositionFrame.PositionFrame(debugger), \
				WatchesFrame.WatchesFrame(debugger), \
				BreakpointsFrame.BreakpointsFrame(debugger) ]

		#Register callback after frames!
		self.debugger.gotActiveCallback += [self.updateValues]

		#First paned window
		self.paned1 = gtk.VPaned()
		vbox.add(self.paned1)
		#Second one
		self.paned2 = gtk.VPaned()
		self.paned1.add2(self.paned2)

		self.paned1.add1(self.frames[1])
		self.paned2.add1(self.frames[2])
		self.paned2.add2(self.frames[0])

		self.show_all()


	def applyConfiguration(self, conf):

		w = conf.findInt("statuswnd-width")
		h = conf.findInt("statuswnd-height")
		paned1 = conf.findInt("statuswnd-paned1")
		paned2 = conf.findInt("statuswnd-paned2")

		if w!=None and h!=None:
			self.resize(w,h)
		if paned1!=None:
			self.paned1.set_position(paned1)
		if paned2!=None:
			self.paned2.set_position(paned2)


		while not self.debugger.isActive():
			gtk.main_iteration()

		for f in self.frames:
			f.applyConfiguration(conf)


	def fillConfiguration(self, conf):

		conf.addInt("statuswnd-width", self.get_size()[0])
		conf.addInt("statuswnd-height", self.get_size()[1])
		conf.addInt("statuswnd-paned1", self.paned1.get_position())
		conf.addInt("statuswnd-paned2", self.paned2.get_position())

		conf.setCommand( self.debugger.clientCmd )

		for f in self.frames:
			f.fillConfiguration(conf)


	def updateValues(self, status, param):

		conf = Configuration.Configuration()
		self.fillConfiguration(conf)
		conf.store(".pygdb.conf")

		self.updateVim()


	def updateVim(self):

		os.system('gvim --servername %s --remote-send "<ESC> :GDBLoadConfig<CR>"' % \
			self.vimservername)


