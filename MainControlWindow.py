#!/usr/bin/python
#shuber, 2008-06-04

__author__ = "shuber"


import gtk
import string
import sys
import vte


import DbgTerminal
import ClientIOTerminal


class MainControlWindow (gtk.Window):

	def __init__(self, dbgterm):

		#Set up GTK stuff
		gtk.Window.__init__(self)
		self.connect("destroy", DbgTerminal.quitHandler )

		dbgterm.gotActiveCallback += [self.enableButtons]
		dbgterm.gotInactiveCallback += [self.disableButtons]

		#Set terminals
		self.dbgterm = dbgterm
		self.clientioterm = ClientIOTerminal.ClientIOTerminal(self.dbgterm.client_ptymaster)

		#Set title and add terminal
		self.set_title("Main Control")
		self.set_border_width(5)
			

		#Vertical box. Top: Buttons, Bottom: Terminal vpane
		vbox = gtk.VBox(False,5)
		self.add(vbox)

		#Button box
		hbtnbox = gtk.HBox(False, spacing=5)
		#hbtnbox.set_layout(gtk.BUTTONBOX_START)
		vbox.pack_start(hbtnbox)

		self.runBtn = gtk.Button("Run")
		hbtnbox.add(self.runBtn)
		self.continueBtn = gtk.Button("Continue")
		hbtnbox.add(self.continueBtn)
		self.stepoverBtn = gtk.Button("Step Over")
		hbtnbox.add(self.stepoverBtn)
		self.stepinBtn = gtk.Button("Step In")
		hbtnbox.add(self.stepinBtn)
		self.stepoutBtn = gtk.Button("Step Out")
		hbtnbox.add(self.stepoutBtn)
		self.quitBtn = gtk.Button("Quit")
		hbtnbox.add(self.quitBtn)

		#Vertical pane for terminals
		vpaned = gtk.VPaned()
		vbox.pack_start(vpaned, True, True)
		vpaned.add(self.dbgterm)
		vpaned.add(self.clientioterm)


		#Install handlers
		self.runBtnHandler = self.runBtn.connect('clicked', self.runBtnClicked)
		self.continueBtnHandler = self.continueBtn.connect('clicked', \
				self.continueBtnClicked)
		self.stepoverBtnHandler = self.stepoverBtn.connect('clicked', \
				self.stepoverBtnClicked)
		self.stepinBtnHandler = self.stepinBtn.connect('clicked', self.stepinBtnClicked)
		self.stepoutBtnHandler = self.stepoutBtn.connect('clicked', self.stepoutBtnClicked)
		self.quitBtnHandler = self.quitBtn.connect('clicked', self.quitBtnClicked)

		#Show the window
		self.show_all()



	def runBtnClicked(self, btn):
		pos = self.dbgterm.setRun()

	def continueBtnClicked(self, btn):
		pos = self.dbgterm.setContinue()

	def stepoverBtnClicked(self, btn):
		pos = self.dbgterm.setStepover()

	def stepinBtnClicked(self, btn):
		pos = self.dbgterm.setStepin()

	def stepoutBtnClicked(self, btn):
		pos = self.dbgterm.setStepout()

	def quitBtnClicked(self, btn):
		self.dbgterm.setQuit()

	def disableButtons(self, *w):
		self.runBtn.handler_block(self.runBtnHandler)
		self.continueBtn.handler_block(self.continueBtnHandler)
		self.stepoverBtn.handler_block(self.stepoverBtnHandler)
		self.stepinBtn.handler_block(self.stepinBtnHandler)
		self.stepoutBtn.handler_block(self.stepoutBtnHandler)
		self.quitBtn.handler_block(self.quitBtnHandler)

	def enableButtons(self, *w):
		self.runBtn.handler_unblock(self.runBtnHandler)
		self.continueBtn.handler_unblock(self.continueBtnHandler)
		self.stepoverBtn.handler_unblock(self.stepoverBtnHandler)
		self.stepinBtn.handler_unblock(self.stepinBtnHandler)
		self.stepoutBtn.handler_unblock(self.stepoutBtnHandler)
		self.quitBtn.handler_unblock(self.quitBtnHandler)

