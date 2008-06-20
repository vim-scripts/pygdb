#!/usr/bin/python
#shuber, 2008-06-09

__author__ = "shuber"



import re
import string

import StatusWindow

class Configuration:

	def __init__(self):
		self.clear()


	def clear(self):
		self.breakpoints = []
		self.watches = []
		self.ints = []
		self.currfile, self.currlineno = None, 0


	def load(self, filename):
		try:
			self.clear()

			cnt = 0
			#Parse all lines
			f = file(filename, "r")
			for line in f.readlines():
				cnt += 1

				#Get command and tail
				cmd = string.split(line)[0]
				tail = string.join(string.split(line)[1:])
				
				if cmd == "break":
					self.parseBreak(tail)
				elif cmd == "watch":
					self.parseWatch(tail)
				elif cmd == "int":
					self.parseInt(tail)
				elif cmd == "currpos":
					self.parseCurrpos(tail)
				else:
					cnt -= 1
					print "Unkown command", cmd
			f.close()
			return cnt

		except IOError:
			return None


	def store(self, filename):
		try:
			f = file(filename, "w")

			for b in self.breakpoints:
				self.__writeBreak(f, b)

			for w in self.watches:
				self.__writeWatch(f, w)

			for s in self.ints:
				self.__writeInt(f, s)

			if self.isCurrposSet():
				self.__writeCurrpos(f)

			f.close()
			return True

		except IOError:
			return False



	def parseBreak(self, tail):

		tail = tail.strip()
		rx = re.compile("^[\w/\._\-]+:\d+(\s+if\s+\S+.*)?$")

		if not rx.search(tail):
			print "Wrong breakpoint format:", tail
			return

		preif = string.split(tail, " if ")[0].strip()
		postif = string.join( string.split(tail, " if ")[1:], " if ").strip()

		[file,lineno] = string.split(preif, ":")
		lineno = int(lineno)

		cond = None
		if postif != "":
			cond = postif

		self.addBreak(file, lineno, cond)

	def parseInt(self, tail):
		tail.strip()
		rx = re.compile("^[\w_\-]+\s+\d+$")

		if not rx.search(tail):
			print "Wrong size format:", tail
			return

		[name,val] = string.split(tail)
		val = int(val)
		self.addInt(name, val)

	def parseWatch(self, tail):
		self.addWatch(tail)

	def parseCurrpos(self, tail):

		tail = tail.strip()
		rx = re.compile("^[\w/\._\-]+:\d+$")

		if not rx.search(tail):
			print "Wrong current position format:", tail
			return

		[file,lineno] = string.split(tail, ":")
		lineno = int(lineno)

		self.setCurrpos(file, lineno)


	def __writeBreak(self, f, b):
		if b["cond"] != None:
			f.write("break %(file)s:%(lineno)d if %(cond)s\n" % b)
		else:
			f.write("break %(file)s:%(lineno)d\n" % b)

	def __writeInt(self, f, s):
		f.write("int %(name)s %(val)d\n" % s)

	def __writeWatch(self, f, w):
		f.write("watch %(expr)s\n" % w)

	def __writeCurrpos(self, f):
		f.write("currpos %s:%d\n" % (self.currfile, self.currlineno))


	def addBreak(self, file, lineno, cond=None):
		bp = {"file" : file, "lineno" : lineno, "cond" : cond}
		if not bp in self.breakpoints:
			self.breakpoints += [bp]

	def addInt(self, name, val):
		i = {"name": name, "val": val}
		if not i in self.ints:
			self.ints += [i]

	def addWatch(self, expr):
		w = {"expr" : expr.strip() }
		if not w in self.watches:
			self.watches += [w]

	def setCurrpos(self, file, lineno):
		self.currfile, self.currlineno = file, lineno

	def isCurrposSet(self):
		return self.currfile!=None

	def delCurrpos(self):
		self.currfile = None


	def findInt(self, name):
		for i in self.ints:
			if i["name"] == name:
				return i["val"]
		return None


	def __str__(self):
		return "breakpoints=" + str(self.breakpoints) + \
				", watches=" + str(self.watches) + \
				", ints=" + str(self.ints) + \
				", currpos=" + str((self.currfile, self.currlineno))



