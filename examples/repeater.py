#!/usr/bin/env python
# -*- coding: utf-8 -*-

import tweebot


class Repeater(tweebot.Context):
	def __init__(self, *args, **kwargs):
		settings = {
			'app_name'             : 'repeater',
			#'username'             : '<YOUR ACCOUNT NAME>',
			#'consumer_key'         : '<YOUR CONSUMER KEY>',
			#'consumer_secret'      : '<YOUR CONSUMER SECRET>',
			#'access_key'           : '<YOUR ACCESS KEY>',
			#'access_secret'        : '<YOUR ACCESS SECRET>',
			'timeout'              : 1 * 60, # 1 min
			'history_file'         : 'repeater.history',
			'log_file_prefix'      : 'repeater.log',
			'log_file_max_size'    : 1024 * 1024 * 10,
			'log_file_num_backups' : 5,
		}
		super(Repeater, self).__init__(settings)

def main():
	bot = Repeater()
	tweebot.enable_logging(bot)
	bot.start_forever(
		tweebot.SearchMentions(),
		tweebot.MultiPart.And(
			tweebot.BaseFilter,
			tweebot.UsersFilter.Friends(reload_every=100),
			tweebot.BadTweetFilter),
		tweebot.ReplyRetweet)

if __name__ == '__main__':
	main()
