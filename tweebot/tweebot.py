#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# MIT License
# Copyright (c) 2011 Maxim Kamenkov
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
import re
import time
import random
import operator
import logging
import logging.handlers
import tweepy

try:
	import simplejson as json
except ImportError:
	try:
		import json
	except ImportError:
		try:
			from django.utils import simplejson as json  # Google App Engine?
		except ImportError:
			raise ImportError, 'json library is not installed'


__all__ = [
	'enable_logging', 'Settings', 'Replies', 'Context', 'MultiPart',
	'SearchQuery', 'SearchMentions', 'BaseFilter', 'FriendsOnlyFilter',
	'BadTweetFilter', 'ReplyRetweet', 'ReplyTemplate',]


def enable_logging(context):
	'''Turns on formated logging output based on provided settings
	from context. Stdout will be used by default if no settings has
	been given.
	'''
	settings = context.settings
	root_logger = logging.getLogger()
	if settings.get('logging') == 'none':
		# logging has been disabled by user
		return root_logger
	level = getattr(logging, settings.get('logging', 'info').upper())
	root_logger.setLevel(level)
	formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s')
	if settings.get('log_file_prefix'):
		channel = logging.handlers.RotatingFileHandler(
			filename=settings.log_file_prefix,
			maxBytes=settings.log_file_max_size,
			backupCount=settings.log_file_num_backups)
		channel.setFormatter(formatter)
		root_logger.addHandler(channel)
	if settings.get('log_to_stderr') or \
		('log_to_stderr' not in settings and not root_logger.handlers):
		channel = logging.StreamHandler()
		channel.setFormatter(formatter)
		root_logger.addHandler(channel)
	return root_logger


def _author(entity, details=False, default=None):
	'''Helper to unify access to author's info in different Models.

	If `details` set to True will return tuple (name, id) otherwise
	will return only name.
	'''
	# check for `status` Model
	if hasattr(entity, 'author'):
		a = entity.author
		return details and (a.screen_name, a.id) or a.screen_name
	# else check for `search result` Model
	if hasattr(entity, 'from_user'):
		return details and (entity.from_user, entity.from_user_id) or entity.from_user
	# so, use default
	return default


class Settings(dict):
	'''Context's settings, an dictionary with object-like access.
	This class allows create hierarchical structure for your settings.
	'''
	@classmethod
	def merge_settings(cls, *args):
		res = {}
		for arg in args:
			if isinstance(arg, dict):
				res.update(arg.copy())
		return res

	@classmethod
	def default_settings(cls):
		'''Returns default settings thats can be userd as parent for
		your ones.
		'''
		if not hasattr(cls, '_default_setttings'):
			cls._default_setttings = cls({
				'logging'              : 'info',
				'history_file'         : 'replyed.json',
				'log_to_stderr'        : True,
				'log_file_prefix'      : False,
				'log_file_max_size'    : 1024 * 1024 * 64,
				'log_file_num_backups' : 4,
				'timeout'              : 30 * 60,
				'bloked_users'         : [],
				'bloked_words'         : [],
			})
			return cls._default_setttings

	def __init__(self, settings=None, parent_settings=None):
		if settings is None:
			settings = {}
		if parent_settings is None:
			parent_settings = {}
		dict.__init__(self, self.merge_settings(parent_settings, settings))
		self._parent_settings = parent_settings

	def __getattr__(self, key):
		try:
			return self[key]
		except KeyError, ex:
			raise AttributeError, ex

	def __setattr__(self, key, value):
		self[key] = value

	def __delattr__(self, key):
		try:
			del self[key]
		except KeyError, ex:
			raise AttributeError, ex

	def __repr__(self):
		return '<Settings %s>' % dict.__repr__(self)


class Replies(list):
	'''Simple history class with python list interface. The history
	will be saved/loaded to/from text file in JSON format. You can
	override save()/load() methods to provide other way to persist
	data.

	If `auto_load` parameter set to True data will be loaded
	automaticaly otherwise load() method should be called manually.
	Also you can `limit` number of ids that will be saved to file.
	'''
	def __init__(self, name, auto_load=True, limit=None):
		super(Replies, self).__init__()
		self.name = name
		self.limit = limit
		if auto_load:
			self.load(limit=limit)

	def load(self, limit=None):
		try:
			f = open(self.name)
			try:
				self.extend(json.loads(f.read())[:limit or self.limit])
			finally:
				f.close()
		except Exception, e: # IOError, JSONDecodeError
			logging.error('Filed to load history | %s' % str(e))

	def save(self, limit=None):
		try:
			f = open(self.name, 'w')
			try:
				# prefer newest ids, it will be helpful to track
				# replyed tweets:
				#
				# >> if max(history) > current_id:
				# >> 	print 'current_id should be skipped'
				#
				recent_first = sorted(self, reverse=True)
				f.write(json.dumps(recent_first[:limit or self.limit]))
			finally:
				f.close()
		except IOError, e:
			logging.error('Filed to save history | %s' % str(e))


class Context(object):
	'''Base Twitter Bot class. The class provides context-sensitive
	data that will be used in Filters, Selectors, Payloads and etc.
	It works like glue between all bot's bloks.
	'''
	def __init__(self, settings, *args, **kwargs):
		if not isinstance(settings, Settings):
			settings = Settings(settings, parent_settings=Settings.default_settings())
		self.settings = settings

	def get_api(self):
		'''Returns configured tweepy API object.'''
		if not hasattr(self, '_api'):
			auth = tweepy.OAuthHandler(self.settings.consumer_key, self.settings.consumer_secret)
			auth.set_access_token(self.settings.access_key, self.settings.access_secret)
			self._api, self._auth = tweepy.API(auth), auth
		return self._api
	api = property(get_api)

	def get_history(self, auto_load=True, limit=None):
		'''Returns configured history object.'''
		if not hasattr(self, '_history'):
			self._history = Replies(self.settings.history_file, auto_load=auto_load, limit=limit)
		return self._history
	history = property(get_history)

	def start(self, select, validate, payload, save_history=True):
		try:
			return [payload(self, entity) for entity in select(self) if validate(self, entity)]
		finally:
			if save_history:
				self.history.save()

	def start_forever(self, select, validate, payload, save_history=True):
		try:
			while True:
				logging.info('Started')
				results = self.start(select, validate, payload, save_history=save_history)
				logging.info('Finished | %d' % len(results))
				time.sleep(self.settings.timeout)
		except (KeyboardInterrupt, SystemExit):
			raise
		finally:
			self.history.save()


class MultiPart(object):
	'''It's bot blok's container. This class allow to work with
	several bloks (Selectors, for example) like with single one.
	The main idea that we can reduce results from every given part
	using a reduce operator. Also you can pass `prepare` function,
	this function will be used to handle results before they will
	be reduced.

	For example, filter that allows tweets that match one of the
	two given filters. Filters results will be converted to bool
	type and than reduced:
	>> multi_filter = MultiPart(filter1, filter2,
	...		reduce_operator=operator.or_, prepare=bool)
	>> context.start(selector1, multi_filter, payload1)
	'''
	@classmethod
	def And(cls, *parts):
		return cls(*parts, **dict(reduce_operator=operator.and_))

	@classmethod
	def Or(cls, *parts):
		return cls(*parts, **dict(reduce_operator=operator.or_))

	@classmethod
	def Add(cls, *parts):
		return cls(*parts, **dict(reduce_operator=operator.add))	

	def __init__(self, *parts, **kwargs):
		self.parts = parts
		self.reduce_operator = kwargs.get('reduce_operator') or operator.add
		self.prepare_func = kwargs.get('prepare')

	def prepare(self, result):
		'''You can override this methos to provide global-level
		result preprocessing before reduce operation.
		'''
		if self.prepare_func:
			return self.prepare_func(result)
		return result

	def __call__(self, *args, **kwargs):
		handle_results = lambda p: self.prepare(p(*args, **kwargs))
		return reduce(self.reduce_operator, map(handle_results, self.parts))


def SearchQuery(query, limit=100):
	'''Returns tweets tnats match the given `query`'''
	def search_handler(context):
		try:
			return context.api.search(query)[:limit]
		except tweepy.error.TweepError, e:
			logging.error('Filed to search query `%s` | %s' % (query, str(e)))
			return []
	return search_handler

def SearchMentions(limit=100):
	'''Returns the mentions of the current user'''
	def search_handler(context):
		try:
			mentions = tweepy.Cursor(context.api.mentions).items(limit=limit)
			return list(mentions)
		except tweepy.error.TweepError, e:
			logging.error('Filed to search mentions | %s' % str(e))
			return []
	return search_handler


def BaseFilter(context, entity):
	'''Filter that excules:
	1. Ours tweets (from user whose name is given in settings).
	2. Tweets from blocked users.
	3. Tweets that already have been answered (tweet_id saved in history).
	'''
	settings = context.settings
	reply_id, reply_to = entity.id, _author(entity)
	if reply_to == settings.get('username'):
		return False
	if reply_to.lower() in settings.get('bloked_users', []):
		return False
	if reply_id in context.history:
		return False
	#if max(context.history) > reply_id:
	#	return False
	return True

def BadTweetFilter(context, entity):
	'''Filter that excules tweets with invalid content.'''
	bloked_words = set(context.settings.get('bloked_words', []))
	normalized_tweet = entity.text.lower().strip()
	tweet_parts = normalized_tweet.split()
	username_count = normalized_tweet.count('@')
	# if contains bloked words
	if bloked_words & set(tweet_parts):
		return False
	# if contains more usernames than words
	if username_count >= len(tweet_parts) - username_count:
		return False
	# if contains author mentions
	#if tweet_parts.count('@'+ _author(entity, default='').lower()) > 0:
	#	return False
	return True

class FriendsOnlyFilter(object):
	'''Filter that allows only tweets from current user's friends'''
	def __init__(self, reload_every=100, *args, **kwargs):
		# friends list will be refreshed for every `reload_every` call
		self.reload_every = reload_every
		self.friends = None
		self.was_error = False
		self._calls = 0 # current num. of calls

	def relaod_friends(self, context):
		try:
			self.friends = context.api.friends_ids()
			self.was_error = False
		except tweepy.error.TweepError, e:
			logging.warning(str(e))
			self.was_error = True

	def __call__(self, context, entity):
		self._calls += 1
		need_reload = self._calls >= self.reload_every
		if self.friends is None or need_reload or self.was_error:
			self.relaod_friends(context)
			if need_reload:
				self._calls = 0
		_, author_id = _author(entity, details=True, default=(0,0))
		return self.friends and author_id in self.friends


def ReplyRetweet(context, entity):
	'''Just retweets given tweet.'''
	reply_id = entity.id
	try:
		result = context.api.retweet(reply_id)
		logging.info('Retweeted | %s ' % reply_id)
		context.history.append(reply_id)
		return result
	except tweepy.error.TweepError, e:
		logging.error('%s | %s' % (reply_id, str(e)))
		return False

class ReplyTemplate(object):
	'''Replies with one of the given template'''
	@classmethod
	def validate_templates(cls, templates):
		if not hasattr(templates, '__iter__'):
			return []
		valid_templates = []
		for tmpl in templates:
			try:
				# we should include @username in reply
				tmpl % ('just for test',)
				valid_templates.append(tmpl)
			except:
				logging.error('Invalid template: %s' % tmpl)
		return valid_templates

	def __init__(self, templates):
		self.templates = self.validate_templates(templates)

	def reply_template(self, context, entity):
		return random.choice(self.templates) % _author(entity)

	def __call__(self, context, entity):
		reply_id = entity.id
		answer = self.reply_template(context, entity)
		try:
			result = context.api.update_status(answer, reply_id)
			context.history.append(reply_id)
			logging.info('%s | Reply: %s' % (reply_id, answer))
			return result
		except tweepy.error.TweepError, e:
			logging.error('%s | %s | %s' % (reply_id, str(e), answer))
			return False


class Condition(object):
	'''Conditional payload part. Child part (payloads only) will
	be executed only if this condition is suitable for given
	context and entity, otherwise `default_result` will be returned.
	'''
	def __init__(self, payload_part, default_result=None):
		self.part = payload_part
		self.default_result = default_result

	def is_suitable(self, context, entity):
		'''Override this method to implement specific rule.

		Say for example, child part should be executed for entity
		with text length == 10. It should look like this:

		def is_suitable(self, ctx, entity):
			return len(entity.text) == 10
		'''
		return True

	def handle(self, context, entity):
		return self.part(context, entiry)

	def __call__(self, context, entity):
		if self.is_suitable(cntext, entity):
			return self.handle(context, entity)
		return self.default_result

class RegexpCondition(Condition):
	'''Executes for tweet that matches to given regexp'''
	def __init__(self, payload_part, regexp, *args, **kwargs):
		super(RegexpCondition, self).__init__(payload_part, *args, **kwargs)
		self.regexp = regexp

	def is_suitable(self, context, entity):
		# note that we are looking w/o any `re` flags
		return re.search(self.reqexp, entity.text)
