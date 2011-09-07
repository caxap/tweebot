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
import tweebot


class RepeaterBot(tweebot.Context):
	def __init__(self, *args, **kwargs):
		settings = {
			'app_name'             : 'repeater',
			#'username'             : '<YOUR ACCOUNT NAME>',
			#'consumer_key'         : '<YOUR CONSUMER KEY>',
			#'consumer_secret'      : '<YOUR CONSUMER SECRET>',
			#'access_key'           : '<YOUR ACCESS KEY>',
			#'access_secret'        : '<YOUR ACCESS SECRET>',
			'timeout'              : 1 * 60, # 15 min
			'history_file'         : 'repeater.history',
			'log_file_prefix'      : 'repeater.log',
			'log_file_max_size'    : 1024 * 1024 * 10,
			'log_file_num_backups' : 5,
		}
		super(RepeaterBot, self).__init__(settings)

def main():
	bot = RepeaterBot()
	tweebot.enable_logging(bot)
	bot.start_forever(
		tweebot.SearchMentions(),
		tweebot.MultiPart.And(
			tweebot.BaseFilter,
			tweebot.FriendsOnlyFilter(reload_every=100),
			tweebot.BadTweetFilter),
		tweebot.ReplyRetweet)

if __name__ == '__main__':
	main()