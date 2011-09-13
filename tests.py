#!/usr/bin/env python
#-*- coding: utf-8 -*-
# MIT License
# Copyright (c) 2011 Maxim Kamenkov
import time
import random
import unittest
import tweebot

class SettingsTests(unittest.TestCase):

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

#
# Other tests comming soon... :)
#

if __name__ == '__main__':
	unittest.main()
