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

TEMPLATES = [
'Have a good day @%s!',
'Well done @%s!',
'You are so sweety @%s!',
'You are so amazing @%s!',
'Your beauty is amazing @%s!',
'You look well @%s!',
'It\'s a pleasure to talk to you @%s!',
'You are an intelligent person @%s!',
'It\'s a pleasure to deal with you @%s!',
'You look wonderful @%s!',
'You are charming @%s!',
'You look lovely @%s!',
'How are you @%s?',
]

class ComplementorBot(tweebot.Context):
	def __init__(self, *args, **kwargs):
		settings = {
			'app_name'       : 'complementor',
			#'username'       : '<YOUR ACCOUNT NAME>',
			#'consumer_key'   : '<YOUR CONSUMER KEY>',
			#'consumer_secret': '<YOUR CONSUMER SECRET>',
			#'access_key'     : '<YOUR ACCESS KEY>',
			#'access_secret'  : '<YOUR ACCESS SECRET>',
			'timeout'        : 30 * 60, # 30 min
			'history_file'   : 'complementor.history'
		}
		super(ComplementorBot, self).__init__(settings)

def main():
	bot = ComplementorBot()
	tweebot.enable_logging(bot)
	bot.start_forever(
		tweebot.MultiPart.Add(
			tweebot.SearchMentions(),
			tweebot.SearchQuery('complementor', limit=100)),
		tweebot.MultiPart.And(
			tweebot.BaseFilter,
			tweebot.FriendsOnlyFilter(reload_every=100)),
		tweebot.ReplyTemplate(TEMPLATES))

if __name__ == '__main__':
	main()