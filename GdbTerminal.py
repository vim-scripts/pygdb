#!/usr/bin/python
#shuber, 2008-06-04

__author__ = "shuber"


import gtk
import os
import re
import string
import sys
import time

import DbgTerminal


class GdbTerminal (DbgTerminal.DbgTerminal):


	def __init__(self, clientCmd):
		DbgTerminal.DbgTerminal.__init__(self, clientCmd)

	def getArgv(self):
		return ["gdb", "--fullname", string.split(self.clientCmd)[0]]

	def setRun(self):
		argv = string.join(string.split(self.clientCmd)[1:])
		self.feed_child("run " + argv + "\n")

	def setContinue(self):
		self.feed_child("cont\n");

	def setStepover(self):
		self.feed_child("next\n");

	def setStepin(self):
		self.feed_child("step\n");

	def setStepout(self):
		bt = self.getBacktrace()

		if len(bt) < 2:
			self.setContinue()

		else:
			#Get the second line
			sec = bt[1]

			#Check if it is a backtrace line
			if re.compile("^#1\s+.*\s\S+:\d+$").search(sec):
				pos = string.split(sec)[-1]
				self.feed_child("advance %s\n" % pos)


	def setQuit(self):
		self.feed_child("quit\n")
		self.waitForNewline()
		self.feed_child("y\n");

	def setPty(self, pty):
		ttyname = os.ttyname(pty)
		self.__getAnswerFromCmd("set inferior-tty %s\n" % (ttyname,))

	def setBreakpoint(self, file, lineno, condition=None):
		his = self.getHistoryLen()
		if condition==None:
			self.feed_child("break %s:%s\n" % (file, str(lineno)))
		else:
			self.feed_child("break %s:%s if %s\n" % \
					(file, str(lineno), condition))

		rx = "^Breakpoint |^No |^\(gdb\) "
		his, response = self.waitForRx(rx, his)

		answer = None

		if response[0:10] == "Breakpoint":
			answer = string.split(response)[1].strip()
		
		#Wants an answer: "No"
		if response[0:14] == "No source file":
			self.feed_child("n\n");

		#Wait again for (gdb)...
		self.waitForPrompt(his)

		return answer


	def delBreakpoint(self, breakpoint):
		self.__getAnswerFromCmd("del breakpoint %s\n" % (breakpoint,))


	def getBreakpoints(self):
		bplines = self.__getAnswerFromCmd("info breakpoints\n")

		rxbp = re.compile("^\d+\s+breakpoint")
		rxpos = re.compile("^.*at \S+:\d+$")
		rxcond = re.compile("^\s+stop only if")

		bpnts = []
		i = 1

		#Parse the resulting lines
		while i<len(bplines):
			line = bplines[i]

			if not rxbp.search(line):
				i += 1
				continue
	
			#Get number of breakpoint
			no = string.split(line)[0]

			#This line does not contain the file!
			#Check for next line...
			if not rxpos.search(line):
				i += 1
			if not rxpos.search(line):
				i += 1
				continue

			pos = string.split(line)[-1]
			[file,lineno] = string.split(pos,":")
			cond = None

			#Look for conditions
			if i+1<len(bplines) and rxcond.search(bplines[i+1]):
				i +=1
				line = bplines[i]
				cond = string.join(string.split(line," if ")[1:], " if ")
				cond = cond.strip()

			bpnts += [[no, file, lineno, cond]]
			i += 1

		return bpnts
		


	def getExpression(self, expr):
		answer = self.__getAnswerFromCmd("print " + expr + "\n")
		answer = answer[-1]

		if len(string.split(answer, "=")) == 1:
			return answer.strip()

		split = string.split(answer, "=")
		return string.join(split[1:], "=").strip()

	
	def listCodeSnippet(self):
		return self.__getAnswerFromCmd("list\n")

	def getBacktrace(self):
		return self.__getAnswerFromCmd("bt\n")

	def waitForPrompt(self, his):
		rx = "^\(gdb\)"
		return self.waitForRx(rx,his)

	def __getAnswerFromCmd(self, cmd):
		starthis = self.getHistoryLen()
		self.feed_child(cmd)
		endhis, response = self.waitForPrompt(starthis)

		return self.history[starthis:endhis]


	def testForActivity(self, his):
		"""Test whether debugger got active again"""
			
		line = self.history[his]

		if string.find(line, "\x1a\x1a") == 0:
			tuples = string.split(line[2:], ":")
			tuples[1] = int(tuples[1])
			return "break", [tuples[0], int(tuples[1])]

		if string.find(line, "Program exited") == 0:
			code = string.split(line)[-1]

			codeno = 0
		
			#Parse the octal number
			if code[0] == "O":
				code = code[1:-1]
				for c in code:
					codeno = codeno*8 + int(c)

			return "exited", codeno

		return None


	def testForInactivity(self, his):
		"""Test whether debugger got inactive"""		
		line = self.history[his]

		if string.find(line, "Starting program:") == 0:
			prog = string.join( string.split(line)[1:])
			return "started", prog

		if string.find(line, "Continuing.") == 0:
			return "continued", None

		if string.find(line, "\x1a\x1a") == 0:
			rxcont = re.compile("^\(gdb\)\s+(cont|step|next|stepi|nexti|advance)")

			if rxcont.search(self.history[his-1]):
				return "stepped", None
			if rxcont.search(self.history[his-2]):
				return "stepped", None

		return None








if __name__ == "__main__":


	dbgterm = GdbTerminal(string.join(sys.argv[1:]))
	dbgwnd = DbgTerminal.DbgWindow(dbgterm)

	gtk.main()




