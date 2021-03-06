TweeBot v1.0
============
A Python library to build twitter bots over tweepy library. It's a very simple 
and flexible way to create your own bot.


Example
=======

```python
# Next code demonstrates how to create simple twitter bot that select all friends'
# tweets with your mentiones and retweet they. (See comments in code for more 
# details about how filters work.)

import tweebot as twb

def main():
    # Step 1. setup context configuration
    repeater = twb.Context({
		'app_name'        : 'repeater',
		'username'        : '<YOUR ACCOUNT NAME>',
		'consumer_key'    : '<YOUR CONSUMER KEY>',
		'consumer_secret' : '<YOUR CONSUMER SECRET>',
		'access_key'      : '<YOUR ACCESS KEY>',
		'access_secret'   : '<YOUR ACCESS SECRET>',
		'timeout'         : 1 * 60, # 1 min, ensure twitter api limits
		'history_file'    : 'history.json',
	})

	# Step 2. enable pretty logging
	twb.enable_logging(repeater)

	# Step 3. setup chain Selector->Filters->Action
	chain = (
		twb.SearchMentions(),
		twb.MultiPart.And(
			twb.BaseFilter,
			twb.UsersFilter.Friends(),
			twb.BadTweetFilter),
		twb.ReplyRetweet)

	# Step 4. start processing 
	repeater.start_forever(*chain)

if __name__ == '__main__':
	main()
```

Other
=====

* **Bug tracker**: <http://github.com/caxap/tweebot/issues>
* **Souce code**: <http://github.com/caxap/tweebot>
* **Dependencies**:
    - Python 2.5 or newer (<3.0)
    - Tweepy <http://github.com/joshthecoder/tweepy>
    - Simplejson <http://undefined.org/python/#simplejson> (Included in python 2.6+)
