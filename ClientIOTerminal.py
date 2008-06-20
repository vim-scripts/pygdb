#!/usr/bin/python
#shuber, 2008-06-04

__author__ = "shuber"


import gtk
import pango
import vte


class ClientIOWindow (gtk.Window):


	def __init__(self, parent, pty_master):

		#Set up GTK stuff
		gtk.Window.__init__(self)
		self.set_screen(parent.get_screen())


		#Set title and add terminal
		self.set_title("Client I/O")
		self.terminal = ClientIOTerminal(pty_master)
		self.add(self.terminal)

	
		#Show the window
		self.show_all()



class ClientIOTerminal(vte.Terminal):

	def __init__(self, pty_master):
		vte.Terminal.__init__(self)
		self.set_pty(pty_master)

		fontdesc = pango.FontDescription("monospace 9")
		self.set_font(fontdesc)


