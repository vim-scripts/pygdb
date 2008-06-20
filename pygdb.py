#!/usr/bin/python
#shuber, 2008-06-08

__author__ = "shuber"

import gtk
import os
import string
import sys

import Configuration
import DbgTerminal
import GdbTerminal
import MainControlWindow
import StatusWindow


def launchDebugger(clientCmd):

	#Create Terminal
	dbgterm = GdbTerminal.GdbTerminal(clientCmd)

	#Create windows
	mainCtrlWnd = MainControlWindow.MainControlWindow(dbgterm)
	statusWnd = StatusWindow.StatusWindow(dbgterm)
	dbgterm.initialize()

	#Load configuration
	conf = Configuration.Configuration()
	conf.load(".pygdb.conf")
	statusWnd.applyConfiguration(conf)
	
	gtk.main()

	#Store config
	conf = Configuration.Configuration()
	statusWnd.fillConfiguration(conf)
	conf.delCurrpos()
	conf.store(".pygdb.conf")
		
	DbgTerminal.updateVim()



if __name__ == "__main__":

	#Check if enough arguments are given
	if len(sys.argv) <= 1:
		print "Please give executeable to debug."
		sys.exit(-1)

	#Create the terminals
	clientCmd = string.join(sys.argv[1:])
	launchDebugger(clientCmd)


