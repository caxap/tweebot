#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
This is simple Twitter Bot that sends "Thanks for Following"
replies to every new follower.
'''

import tweebot

# Feel free to add more templates 
TEMPLATES = ["@%s, Thanks for Following!", ]


def SelectFollowers(context):
	# Cursor wrapper can be used here, but for demo we ok with
	# current implementation
	try:
		users_ids = context.api.followers_ids()
		return context.api.lookup_users(user_ids=users_ids[:100])
	except Exception, e: # Tweepy error
		logging.error('Failed to select followers %s' % str(e))
		return []


class ReplyTemplateDirect(tweebot.ReplyTemplate):
	'''Sends direct message generated from template'''
	def reply(self, context, user_id, text):
		return context.api.send_direct_message(user_id=user_id, text=text)


class ThanksForFollowing(tweebot.Context):
	def __init__(self, *args, **kwargs):
		settings = {
			'app_name'       : 'thanks_follow',
			#'username'       : '<YOUR ACCOUNT NAME>',
			#'consumer_key'   : '<YOUR CONSUMER KEY>',
			#'consumer_secret': '<YOUR CONSUMER SECRET>',
			#'access_key'     : '<YOUR ACCESS KEY>',
			#'access_secret'  : '<YOUR ACCESS SECRET>',
			'timeout'        : 20 * 60, # check every 20 min
			'history_file'   : 'thanks_follow.history'
		}
		super(ThanksForFollowing, self).__init__(settings)


def main():
	bot = ThanksForFollowing()
	tweebot.enable_logging(bot)
	bot.start_forever(
		SelectFollowers,
		tweebot.BaseFilter,
		ReplyTemplateDirect(TEMPLATES))


if __name__ == '__main__':
	main()
