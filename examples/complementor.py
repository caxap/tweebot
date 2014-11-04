#!/usr/bin/env python
# -*- coding: utf-8 -*-

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


class Complementor(tweebot.Context):
    def __init__(self, *args, **kwargs):
        settings = {
            'app_name': 'complementor',
            #'username'       : '<YOUR ACCOUNT NAME>',
            #'consumer_key'   : '<YOUR CONSUMER KEY>',
            #'consumer_secret': '<YOUR CONSUMER SECRET>',
            #'access_key'     : '<YOUR ACCESS KEY>',
            #'access_secret'  : '<YOUR ACCESS SECRET>',
            'timeout': 30 * 60,  # 30 min
            'history_file': 'complementor.history'
        }
        super(Complementor, self).__init__(settings)


def main():
    bot = Complementor()
    tweebot.enable_logging(bot)
    bot.start_forever(
        tweebot.MultiPart.Add(
            tweebot.SearchMentions(),
            tweebot.SearchQuery('complementor')),
        tweebot.MultiPart.And(
            tweebot.BaseFilter,
            tweebot.MultiPart.Or(
                tweebot.UsersFilter.Friends(),
                tweebot.UsersFilter.Followers())),
        tweebot.ReplyTemplate(TEMPLATES))

if __name__ == '__main__':
    main()
