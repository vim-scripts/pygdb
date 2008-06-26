"pygdb.vim - pygtk interface to gdb in connection with (g)vim
" Maintainer: Stefan Huber <shuber@cosy.sbg.ac.at>


if !has('python')
	echo "Error: Required vim compiled with +python"
	finish
endif

if ! exists("g:pygdb")

let g:pygdb = 1
let s:ScriptLocation = expand("<sfile>")


python << >>

import gtk
import os
import string
import sys
import threading
import vim

import Configuration
import DbgTerminal



#Breakpoint positions: List of dictionaries of form
#{"signnum" : , "file" : , "lineno":, "cond" : }
gdbBps = []
signnum = 0
clientcmd = ""
execsign = None

def gdbLaunch():
	global gdbBps, clientcmd, pygdbdir

	clientcmd = vim.eval("input('Client commando: ', '%s')" % clientcmd)
	
	#Pressed esq?
	if clientcmd == None:
		clientcmd = ""
		return

	#Strip away white space
	clientcmd = clientcmd.strip()

	if clientcmd.strip()=="":
		print "No command given!"
		return

	#Add the breakpoints to the configuration
	conf = Configuration.Configuration()
	conf.load(".pygdb.conf")
	conf.breakpoints = []
	for bp in gdbBps:
		conf.addBreak(bp["file"], bp["lineno"], bp["cond"])
	conf.store(".pygdb.conf")
	
	vim.command("!python %s/pygdb.py --vim-servername %s %s &\n" % (pygdbdir, vim.eval("v:servername"), clientcmd))


def gdbToggleBreakpoint(lineno=None, file=None):
	global gdbBps

	#Set lineno and file if not already set
	if lineno==None:
		lineno = vim.current.window.cursor[0]
	if file==None:
		file = getCurrentFile()

	#Determine index of breakpoint
	bpidx = gdbGetBreakpoint( file, lineno )

	if bpidx != None:
		removeBreakpoint(bpidx)
	else:
		addBreakpoint(file, lineno)


def setExecutionLine(file, lineno):
	global execsign


	#Open that file!
	if file != getCurrentFile():
		try:
			os.stat(file)
			vim.command(":e %s" % file)
		except OSError:
			print "Warning: file '%s' does not exist! (Wrong client command?)" % file
			return

	#Jump to line
	vim.command(":%d" % lineno)

	#Remove old execsign
	if execsign != None:
		delExecutionLine()

	#Set the sign
	execsign = gdbNewSignnum()
	vim.command("sign place %d line=%s name=ExecutionLine file=%s"%(execsign, lineno, file))


def delExecutionLine():
	global execsign

	#Remove old execsign
	if execsign != None:
		vim.command("sign unplace %d" % execsign)
		execsign = None


def addBreakpoint(file, lineno, cond=None):
	global gdbBps, cmdset

	#If file is not open, open it
	if not file in [b.name for b in vim.buffers]:
		try:
			os.stat(file)
			vim.command(":e %s" % file)
		except OSError:
			print "Warning: file '%s' does not exist! (Wrong client command?)" % file
			cmdset = False
			return


	#Determine a sign number
	signnum = gdbNewSignnum()

	#Create breakpoint and add sign
	b = {"signnum" : signnum, "lineno" : lineno, "file" : file, "cond" : cond}
	gdbBps += [b]

	if cond == None:
		vim.command("sign place %(signnum)d line=%(lineno)d name=BreakPoint file=%(file)s" % b)
	else:
		vim.command("sign place %(signnum)d line=%(lineno)d name=CondBreakPoint file=%(file)s" % b)

		

def removeBreakpoint(idx):
	global gdbBps

	vim.command("sign unplace %(signnum)d" % gdbBps[idx])
	del gdbBps[idx]


def gdbBreakpointCond(lineno=None, file=None, cond=None):
	global gdbBps

	#Set lineno and file if not already set
	if lineno==None:
		lineno = vim.current.window.cursor[0]
	if file==None:
		file = getCurrentFile()

	#Determine index of breakpoint
	bpidx = gdbGetBreakpoint( file, lineno )

	#Alter condition
	if bpidx != None:
		gdbBps[bpidx]["cond"] = vim.eval("input('Breakpoint condition: ', '%s')" % gdbBps[bpidx]["cond"])
	#Set new breakpoint
	else:
		#Get condition
		cond = vim.eval("input('Breakpoint condition: ', '')")
		#Add the breakpoint
		addBreakpoint(file, lineno, cond)


def getCurrentFile():
	return vim.current.window.buffer.name



def gdbNewSignnum():
	global signnum
	signnum += 1
	return signnum


def gdbGetBreakpoint(file, lineno):
	for i in range(len(gdbBps)):
		if [gdbBps[i]["file"], gdbBps[i]["lineno"]] == [file,lineno]:
			return i	
	return None

def gdbShowBreakpoints():
	global gdbBps

	if len(gdbBps) == 0:
		print "No breakpoints set."
	else:
		print "%d breakpoints set:" % len(gdbBps)

	for bp in gdbBps:
		if bp["cond"] != None:
			print "%(file)s:%(lineno)d if %(cond)s" % bp
		else:
			print "%(file)s:%(lineno)d" % bp



def toAbsPath(path):
	global clientcmd, cmdset

	#Not a absolute path --> make one
	if path[0] != os.sep:

		#We need the client command to expand the paths...
		while clientcmd == "" or not cmdset:
			clientcmd = vim.eval("input('Client commando: ', '%s')" % clientcmd)

			if clientcmd == None:
				clientcmd = ""
			clientcmd = clientcmd.strip()

			cmdset = True

		#Get the dirs where executeable is in
		relcmd = string.split(clientcmd)[0]
		abscmd = DbgTerminal.relToAbsPath(getCurrentFile(), relcmd)
		path = DbgTerminal.relToAbsPath(abscmd, path)

		assert(path[0] == "/")

	return path


def gdbLoadConfig():
	global clientcmd, gdbBps, cmdset


	#Load configuration
	conf = Configuration.Configuration()
	conf.load(".pygdb.conf")

	#Remove all breakpoints
	while len(gdbBps)>0:
		removeBreakpoint(0)

	#Add breakpoints from configuration
	for bp in conf.breakpoints:
		bp["file"] = toAbsPath( bp["file"] )
		addBreakpoint(bp["file"], bp["lineno"], bp["cond"])

	#Set the command from config
	if conf.getCommand() != None:
		clientcmd = conf.getCommand()
	
	#Set current execution line
	if conf.isCurrposSet():
		file = toAbsPath(conf.currfile)
		setExecutionLine(file, conf.currlineno)
	else:
		delExecutionLine()

>>

highlight ExecutionLine term=bold ctermbg=DarkGreen ctermfg=Black guibg=LightGreen guifg=Black
highlight BreakPoint term=inverse ctermbg=DarkRed ctermfg=Black guibg=LightRed guifg=Black

sign define ExecutionLine text==> texthl=ExecutionLine linehl=ExecutionLine
sign define BreakPoint text=! texthl=BreakPoint linehl=BreakPoint
sign define CondBreakPoint text=? texthl=BreakPoint linehl=BreakPoint


command! GDBLaunch :python gdbLaunch()
command! GDBToggleBreakpoint :python gdbToggleBreakpoint()
command! GDBBreakpointCond :python gdbBreakpointCond()
command! GDBShowBreakpoints :python gdbShowBreakpoints()
command! GDBLoadConfig :python gdbLoadConfig()



function! GDBMapDefaults()
	nmap <silent> <F5>		:GDBLaunch<CR>
	nmap <silent> <F8>		:GDBToggleBreakpoint<CR>
	nmap <silent> <S-F8>		:GDBBreakpointCond<CR>
	nmap <silent> <F9>		:GDBShowBreakpoints<CR>
	nmap <silent> <S-F9>		:GDBLoadConfig<CR>
endfunction



endif


