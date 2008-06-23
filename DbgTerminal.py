#!/usr/bin/python
#shuber, 2008-06-04

__author__ = "shuber"


import gobject
import gtk
import os
import pango
import pty
import re
import string
import sys
import time
import threading
import vte

import ClientIOTerminal



class DbgTerminal (vte.Terminal):

	def __init__(self, clientCmd):

		vte.Terminal.__init__(self)

		#Set members
		self.childpid = None
		self.history = [""]
		self.isactive = True
		self.lastc, self.lastr = 0,0
		self.gotActiveCallback = []
		self.gotInactiveCallback = []
		self.activityChanged = None

		#Start debugger
		self.clientCmd = clientCmd
		#Open pseudo-terminal where to-be-debugged process reads/writes to
		self.client_ptymaster, self.client_ptyslave = pty.openpty()

		#Set up terminal window and initialize debugger
		self.connect("cursor-moved", self.contents_changed)
		self.connect("child-exited", quitHandler)
		gobject.timeout_add(50, self.checkActivityChanged)

		#font description
		fontdesc = pango.FontDescription("monospace 9")
		self.set_font(fontdesc)


	def initialize(self):
		self.childpid = self.fork_command( self.getCommand(), self.getArgv())
		self.waitForPrompt(0)
		self.setPty(self.client_ptyslave)

	def stopDbg(self):

		if self.childpid != None:
			#9=KILL, 15=TERM
			os.kill(self.childpid, 15);
			self.childpid = None

	def getClientExecuteable(self):
		return string.split(self.clientCmd)[0]


	def toAbsPath(self, path):
		"""convert path to an absolute path relative to the client
		executable we debug."""
		
		#Current working dir
		pwd = os.getcwd() + "/"

		#executeable path
		client = self.getClientExecuteable()
		client = relToAbsPath(pwd, client)		

		return relToAbsPath(client, path)


	def checkActivityChanged(self):

		try:

			#There was activity
			if self.activityChanged != None:

				res = self.activityChanged
				self.activityChanged = None

				status, param = res
				if self.isActive():
					print "got active: ", res
					for cb in self.gotActiveCallback:
						cb(status, param)
				else:
					print "got inactive: ", res
					for cb in self.gotInactiveCallback:
						cb(status, param)
		except Exception, e:
			print e

		return True



	def contents_changed(self, term):
		assert( self.getHistoryLen()>0 )

		c,r = term.get_cursor_position()
		text = self.get_text_range(self.lastr,0,r,c,lambda *w:True)
		self.lastc, self.lastr = c,r

		#Remove annoying \n at the end
		assert(text[-1] == "\n")
		text = text[:-1]

		#Get the lines and remove empty lines
		lines = string.split(text, "\n")

		#Remove the incomplete line
		len = max(0,self.getHistoryLen())
		self.history[-1] = lines[0]
		self.history += lines[1:]


		#Check if activity status has been changed
		for i in range(len, self.getHistoryLen()):
			line = self.history[i]
					
			res = self.testForInactivity(i)
			if res != None:
				while self.activityChanged != None:
					print "wait for pending activity"
					gtk.main_iteration()

				self.setActive(False)
				self.activityChanged = res

			res = self.testForActivity(i)
			if res != None:
				while self.activityChanged != None:
					print "wait for pending activity"
					gtk.main_iteration()

				self.setActive(True)
				self.activityChanged = res




	def waitForNewline(self):
		l = self.getHistoryLen()
		while not self.getHistoryLen() > l:
			gtk.main_iteration()

	def getHistoryLen(self):
		return len(self.history)

	def waitForRx(self, pat, start):	

		rx = re.compile(pat)
		curr = start
		while True:
			assert( curr>=start )
			for no in range(curr, self.getHistoryLen()):
				line = self.history[no]
				if rx.search(line):
					return no, line

			#Do not forget the last line
			curr = max(start,self.getHistoryLen()-1)
			lr, lc = self.lastr, self.lastc

			while (self.lastr, self.lastc) == (lr,lc):
				gtk.main_iteration()


	def getCommand(self):
		return self.getArgv()[0];

	def getArgv(self):
		raise NotImplementedError()

	def setPty(self, pty):
		raise NotImplementedError()

	def setRun(self):
		raise NotImplementedError()

	def setContinue(self):
		raise NotImplementedError()

	def setStepover(self):
		raise NotImplementedError()

	def setStepin(self):
		raise NotImplementedError()

	def setStepout(self):
		raise NotImplementedError()

	def setQuit(self):
		raise NotImplementedError()

	def setBreakpoint(self, file, lineno, condition=False):
		raise NotImplementedError()

	def delBreakpoint(self, breakpoint):
		raise NotImplementedError()

	def getExpression(self, expr):
		raise NotImplementedError()

	def listCodeSnippet(self):
		raise NotImplementedError()

	def getBacktrace(self):
		raise NotImplementedError()

	def waitForPrompt(self, his):		
		raise NotImplementedError()

	def testForActivity(self, his):
		raise NotImplementedError()

	def testForInactivity(self, his):
		raise NotImplementedError()

	def setActive(self, isactive):
		self.isactive = isactive

	def isActive(self):
		return self.isactive

	

def quitHandler(*w):
	try:
		gtk.main_quit()
	except:
		pass


def relToAbsPath(absfile, relfile):
	"""When an absfile is given and a relfile is given by
	relative paths relative to absfile, determine the abs
	path of relfile"""

	#Get directories except for "." parts
	relsplit = filter(lambda x: x!=".", string.split(relfile, os.sep))
	#Get the directories of absfile withouth the trailing filename 
	abssplit = string.split(absfile, os.sep)[:-1]

	#Determine number of ".." and remove them
	up=0
	while relsplit[0] == "..":
		up += 1
		del relsplit[0]
		del abssplit[-1]

	return string.join(abssplit + relsplit, os.sep)


class DbgWindow (gtk.Window):

	clientIOWnd = None


	def __init__(self, terminal):

		#Set up some members
		self.terminal = terminal

		#Set up GTK stuff
		gtk.Window.__init__(self)
		self.connect("destroy", quitHandler)

		#Set title and add terminal
		self.set_title("Debugger I/O")
		self.terminal.history = []
		self.terminal.history_length = 5
		self.add(self.terminal)

		#Show the window
		self.show_all()

	def toggleClientIOWindow(self):
		if not self.clientIOWnd:
			self.clientIOWnd = ClientIOTerminal.ClientIOWindow(self, \
					self.terminal.client_ptymaster)
		else:
			self.clientIOWnd.destroy()
			self.clientIOWnd = None

	def isClientIOWindowExisting(self):
		return self.clientIOWnd != None



