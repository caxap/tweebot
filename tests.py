#!/usr/bin/env python
# -*- coding: utf-8 -*-

import operator
import unittest
import tweebot

# Some helpful utilitest
True_ = lambda *a, **kw: True
False_ = lambda *a, **kw: False
OneTwo = lambda *a, **kw: [1, 2]
ThreeFour = lambda *a, **kw: [3, 4]


class AttrProxy(dict):
    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError


class MockContext(AttrProxy):
    def __init__(self, settings=None, history=None, api=None):
        required_attrs = {
            'settings': AttrProxy(settings or {}),
            'history': history or [],
            'api': AttrProxy(api or {}),
        }
        super(MockContext, self).__init__(required_attrs)


class SettingsTests(unittest.TestCase):
    '''Test tweebot.Settings class'''
    def setUp(self):
        self.settings = tweebot.Settings(
            {'a': 1, 'b': 2, 'c': 3}, parent_settings={'c': 4, 'd': 5})

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
        merged_sett = self.settings.merge_settings(
            {'a': 1}, {'a': 2, 'b': 3}, {'b': 2, 'c': 2})
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
        self.assertEqual(part(), [1, 2, 3, 4])

    def test_prepare(self):
        # count summary lists size
        part = tweebot.MultiPart(
            OneTwo, ThreeFour, prepare=len, reduce_operator=operator.add)
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


class TestBaseFilter(unittest.TestCase):
    '''Test tweebot.BaseFilter class'''
    def setUp(self):
        settings = {'username': 'user1', 'blocked_users': ['user2', 'user3']}
        history = [1, 2, 3]
        self.context = MockContext(settings=settings, history=history)

    def test_myname(self):
        entity1 = AttrProxy(id=0, screen_name='user1')
        self.assertFalse(tweebot.BaseFilter(self.context, entity1))
        entity2 = AttrProxy(id=0, screen_name='user0')
        self.assertTrue(tweebot.BaseFilter(self.context, entity2))

    def test_blockeduser(self):
        entity1 = AttrProxy(id=0, screen_name='user2')
        self.assertFalse(tweebot.BaseFilter(self.context, entity1))
        entity2 = AttrProxy(id=0, screen_name='user3')
        self.assertFalse(tweebot.BaseFilter(self.context, entity2))

    def test_alreadyreplyed(self):
        entity = AttrProxy(id=1, screen_name='user0')
        self.assertFalse(tweebot.BaseFilter(self.context, entity))


class TestBadTweetFilter(unittest.TestCase):
    '''Test tweebot.BadTweetFilter class'''
    def setUp(self):
        settings = {'blocked_words': ['word1', 'word2']}
        self.context = MockContext(settings=settings)

    def test_validtweet(self):
        entity = AttrProxy(id=0, screen_name='user0', text='text')
        self.assertTrue(tweebot.BadTweetFilter(self.context, entity))

    def test_blockedwords(self):
        entity = AttrProxy(id=0, screen_name='user0', text='word1 word2')
        self.assertFalse(tweebot.BadTweetFilter(self.context, entity))

    def test_alotofusernames(self):
        entity = AttrProxy(id=0, screen_name='user0', text='@user0 @user1')
        self.assertFalse(tweebot.BadTweetFilter(self.context, entity))


class TestUsersFilter(unittest.TestCase):
    '''Test tweebot.UsersFilter class'''
    def setUp(self):
        api = {'friends_ids': OneTwo, 'followers_ids': OneTwo}
        self.context = MockContext(api=api)
        self.entity_ok = AttrProxy(id=1, screen_name='user0')
        self.entity_fail = AttrProxy(id=0, screen_name='user0')

    def test_validuser(self):
        filter_ = tweebot.UsersFilter([1, 2])
        self.assertTrue(filter_(self.context, self.entity_ok))

    def test_allowedlist(self):
        filter_ = tweebot.UsersFilter([1, 2])
        self.assertFalse(filter_(self.context, self.entity_fail))

    def test_allowedfunc(self):
        filter_ = tweebot.UsersFilter(OneTwo)
        self.assertTrue(filter_(self.context, self.entity_ok))
        self.assertFalse(filter_(self.context, self.entity_fail))

    def test_followers(self):
        filter_ = tweebot.UsersFilter.Followers()
        self.assertTrue(filter_(self.context, self.entity_ok))
        self.assertFalse(filter_(self.context, self.entity_fail))

    def test_friends(self):
        filter_ = tweebot.UsersFilter.Friends()
        self.assertTrue(filter_(self.context, self.entity_ok))
        self.assertFalse(filter_(self.context, self.entity_fail))

    def test_reloadevery(self):
        self.rotate = False

        def allowed(ctx):
            self.rotate = not self.rotate
            return self.rotate and [1] or [0]

        filter_ = tweebot.UsersFilter(allowed, reload_every=2)
        self.assertTrue(filter_(self.context, self.entity_ok))
        self.assertFalse(filter_(self.context, self.entity_ok))
        self.assertTrue(filter_(self.context, self.entity_fail))
        self.assertFalse(filter_(self.context, self.entity_fail))

    def test_reloadwaserror(self):
        self.rotate = False

        def allowed(ctx):
            self.rotate = not self.rotate
            if self.rotate:
                return [1, 2]
            raise Exception()

        filter_ = tweebot.UsersFilter(allowed, reload_every=1)
        self.assertTrue(filter_(self.context, self.entity_ok))
        self.assertTrue(filter_(self.context, self.entity_ok))
        self.assertTrue(filter_.was_error)
        self.assertFalse(filter_(self.context, self.entity_fail))
        self.assertFalse(filter_.was_error)
        self.assertTrue(filter_(self.context, self.entity_ok))

#
# Other tests comming soon... :)
#

if __name__ == '__main__':
    unittest.main()
