#!/usr/bin/env python
#-*- coding: utf-8 -*-
# MIT License
# Copyright (c) 2011 Maxim Kamenkov
import time
import random
import operator
import unittest
import tweebot

# Some helpful utilitest
True_ = lambda *a, **kw: True
False_ = lambda *a, **kw: False
OneTwo = lambda *a, **kw: [1,2]
ThreeFour = lambda *a, **kw: [3,4]

class AttrProxy(dict):
	def __getattr__(self, key):
		try:
			return self[key]
		except KeyError, ex:
			raise AttributeError, ex


class SettingsTests(unittest.TestCase):
	'''Test tweebot.Settings class'''
	def setUp(self):
		self.settings = tweebot.Settings({'a':1, 'b':2, 'c':3}, parent_settings={'c':4, 'd':5})

	def test_getattr(self):
		self.assertEqual(self.settings.a, 1)
		self.assertEqual(self.settings.b, 2)

	def test_parentattr(self):
		self.assertEqual(self.settings.c, 3)
		self.assertEqual(self.settings.d, 5)

	def test_invalidattr(self):
		self.assertRaises(AttributeError, lambda: self.settings.a_invalid_attr)
		self.assertRaises(AttributeError, lambda: self.settings.b_invalid_attr)

	def test_setattr(self):
		self.settings.e = 1
		self.assertEqual(self.settings.e, 1)
		self.settings.f = 2
		self.assertEqual(self.settings.f, 2)

	def test_delattr(self):
		del self.settings.a
		self.assertRaises(AttributeError, lambda: self.settings.a)
		del self.settings.b
		self.assertRaises(AttributeError, lambda: self.settings.b)

	def test_mergesettings(self):
		merged_sett = self.settings.merge_settings({'a':1}, {'a':2, 'b':3}, {'b':2, 'c':2})
		self.assertEqual(merged_sett['a'], 2)
		self.assertEqual(merged_sett['b'], 2)
		self.assertEqual(merged_sett['c'], 2)

	def test_defaultsettings(self):
		def_sett = self.settings.default_settings()
		def_sett.logging
		def_sett.timeout


class TestMultiPart(unittest.TestCase):
	'''Test tweebot.MultiPart class'''

	def test_and(self):
		part = tweebot.MultiPart.And(True_, False_, True_)
		self.assertFalse(part())

	def test_or(self):
		part = tweebot.MultiPart.Or(True_, False_, True_)
		self.assertTrue(part())

	def test_add(self):
		part = tweebot.MultiPart.Add(OneTwo, ThreeFour)
		self.assertEqual(part(), [1,2,3,4])

	def test_prepare(self):
		#count summary lists size
		part = tweebot.MultiPart(OneTwo, ThreeFour, prepare=len, reduce_operator=operator.add)
		self.assertEqual(part(), 4)

	def test_overrideprepare(self):
		class TestMultiPart(tweebot.MultiPart):
			def prepare(self, result):
				return len(result)
		part = TestMultiPart(OneTwo, ThreeFour, reduce_operator=operator.add)
		self.assertEqual(part(), 4)

class TestCondition(unittest.TestCase):
	'''Test tweebot.Condition, tweebot.RegexpCondition classes'''
	def setUp(self):
		pass

	def test_condition(self):
		cond = tweebot.Condition(False_, default_result=1)
		self.assertFalse(cond(None, None))

	def test_defaultresult(self):
		class FalseCondition(tweebot.Condition):
			def is_suitable(self, *a, **kw):
				return False
		cond = FalseCondition(False_, default_result=1)
		self.assertEqual(cond(None, None), 1)

	def test_regepxcondition(self):
		cond = tweebot.RegexpCondition(False_, r'\d+', default_result=1)
		self.assertFalse(cond(None, AttrProxy(text="abc123")))
		self.assertEqual(cond(None, AttrProxy(text="abc")), 1)

#
# Other tests comming soon... :)
#

if __name__ == '__main__':
	unittest.main()
