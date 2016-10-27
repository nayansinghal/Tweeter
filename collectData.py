###################

# python twitter_stream_download.py -q apple -d data

################

import tweepy
from tweepy import Stream
from tweepy import OAuthHandler
from tweepy.streaming import StreamListener
import time
import argparse
import string
import config
import json
import os
import sys

## parser for command line arguments
def get_parser():
	parser = argparse.ArgumentParser(description="Twitter Downloader")
	parser.add_argument("-q",
						"--query",
						dest="query",
						help="Query/Filter",
						default='-')
	parser.add_argument("-d",
						"--data-dir",
						dest="data_dir",
						help="Output/Data Directory")
	return parser

##  StreamListener for streaming data
class MyListener(StreamListener):

	def __init__(self, data_dir, query):
		query_fname = format_filename(query)
		self.outfile = "%s/stream_%s.json" % (data_dir, query_fname)

	def on_data(self, data):
		try:
			with open(self.outfile, 'a') as f:
				f.write(data)
				print(data)
				return True
		except BaseException as e:
			print("Error on_data: %s" % str(e))
			time.sleep(5)
		return True

	def on_error(self, status):
		print(status)
		print "fail"
		return True

## Convert file name into a safe string
def format_filename(fname):

	return ''.join(convert_valid(one_char) for one_char in fname)

## Convert character into '_' if invalid
def convert_valid(one_char):

	valid_chars = "-_.%s%s" % (string.ascii_letters, string.digits)
	if one_char in valid_chars:
		return one_char
	else:
		return '_'

@classmethod
def parse(cls, api, raw):
	status = cls.first_parse(api, raw)
	setattr(status, 'json', json.dumps(raw))
	return status

def collectData():
	parser = get_parser()
	args = parser.parse_args()
	auth = OAuthHandler(config.consumer_key, config.consumer_secret)
	auth.set_access_token(config.access_token, config.access_secret)
	api = tweepy.API(auth)

	twitter_stream = Stream(auth, MyListener(args.data_dir, args.query))
	twitter_stream.filter(track=[args.query])

if __name__ == '__main__':
	
	collectData()
