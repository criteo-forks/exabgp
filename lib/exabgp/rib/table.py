# encoding: utf-8
"""
table.py

Created by Thomas Mangin on 2009-08-26.
Copyright (c) 2009-2013 Exa Networks. All rights reserved.
"""

import time

# - : remove the route
# + : add a new route
# * : update an existing route (as we use str() and that a route includes the prefix and attributes, may not be used often)

# This is our Adj-RIBs-Out
class Table (object):

	def __init__ (self,peer):
		self.peer = peer
		self.reset()

	def reset (self):
		self._plus = {}
		self._minus = {}

	# This interface is very good for the file change but not if you want to update from network
	def recalculate (self):
		routes = self.peer.neighbor.routes()
		for index in self._plus.keys():
			if index not in routes:
				self._remove(index)
		for route in routes:
			self._add(routes[route])
		return self

	def _add (self,update):
		# XXX: XXX: XXX: FIXME: JUST TEMP - REALLY
		print "\n\nTHIS CODE IS BUGGY and ONLY ALLOW SINGLE NLRI UPDATE\n\n"
		index = update.index(0)
		if index in self._plus:
			if update != self._plus[index][1]:
				self._plus[index] = (time.time(),update,'*')
			return
		self._plus[index] = (time.time(),update,'+')

	def _remove (self,index):
		if index in self._plus:
			self._minus[index] = (time.time(),self._plus[index][1])
			del self._plus[index]

	def changed (self,when):
		"""table.changed must _always_ returns routes to remove before routes to add and must _always_ finish by the time"""
		for index in self._minus:
			t,r = self._minus[index]
			if when < t:
				yield ('-',r)
		for index in self._plus.keys():
			t,r,o = self._plus[index]
			if when < t:
				yield (o,r)
		yield ('',time.time())

	def purge (self,when):
		for index in self._plus.keys():
			t,p = self._plus[index]
			if t < when:
				del self._plus[index]
		for index in self._minus.keys():
			t = self._minus[index]
			if t < when:
				del self._minus[index]
