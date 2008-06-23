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



def getArgs():
	args = {}

	try:

		i=1
		while i < len(sys.argv):

			if sys.argv[i] == "--help":
				args["--help"] = True

			elif sys.argv[i] == "--vim-servername":
				i += 1
				args["--vim-servername"] = sys.argv[i]

			else:
				args["cmd"] = string.join(sys.argv[i:])
				return args

			i += 1

	except Exception, e:
		return False

	return args


def printHelp(f):

	f.write("""Call pygdb with a specific command to be debugged.
	
Usage:
   %s --help
   %s [--vim-servername NAME] <command>

where <command> is the command to call the client that should
be debugged.

  --help
    Print help text.

  --vim-servername NAME
     The servername of the vim to communicate with
""" % (sys.argv[0], sys.argv[0]) )




if __name__ == "__main__":


	#Get the arguments
	args = getArgs()

	if args == None:
		printHelp(sys.stderr)
		sys.exit(-1)
	
	if "--help" in args.keys():
		printHelp(sys.stdout)
		sys.exit(0)

	if not "cmd" in args.keys():
		sys.stderr.write("Please give executeable to debug.")
		sys.exit(-2)

	if "--vim-servername" in args.keys():
		vimservername = args["--vim-servername"]
	else:
		vimservername = "pygdb"



	#Create Terminal
	dbgterm = GdbTerminal.GdbTerminal(args["cmd"])

	#Create windows
	mainCtrlWnd = MainControlWindow.MainControlWindow(dbgterm)
	statusWnd = StatusWindow.StatusWindow(dbgterm, vimservername)
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
		
	statusWnd.updateVim()



