from tweepy import OAuthHandler
from tweepy import API
from tweepy import Cursor
import json
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
from matplotlib import rcParams
from mpltools import style
from matplotlib import dates
from datetime import datetime
import seaborn as sns
import time
import os
from scipy.misc import imread
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
import random
import numpy as np
import sys

# General plotting function for the different information extracted
def plot_tweets_per_category(category, title, x_title, y_title, top_n=5, output_filename="plot.png"):
	"""
	:param category: Category plotted, can be tweets users, tweets language, tweets country etc ..
	:param title: Title of the plot
	:param x_title: List of the items in x
	:param y_title: Title of the variable plotted
	:return: a plot that we can save as pdf or png instead of displaying to the screen
	"""
	tweets_by_cat = category.value_counts()
	fig, ax = plt.subplots()
	ax.tick_params(axis='x')
	ax.tick_params(axis='y')
	ax.set_xlabel(x_title)
	ax.set_ylabel(y_title)
	ax.set_title(title)
	tweets_by_cat[:top_n].plot(ax=ax, kind='bar')
	fig.savefig(output_filename)
	fig.show()

def plot_distribution(category, title, x_title, y_title, output_filename="plot.png"):
		"""
		:param category: Category plotted, can be users, language, country etc ..
		:param title: Title of the plot
		:param x_title: List of the items in x
		:param y_title: Title of the variable plotted
		:return: a plot that we can save as pdf or png instead of displaying to the screen
		"""
		fig, ax = plt.subplots()
		ax.tick_params(axis='x')
		ax.tick_params(axis='y')
		ax.set_xlabel(x_title)
		ax.set_ylabel(y_title)
		ax.set_title(title)
		sns.distplot(category.values, rug=True, hist=True);
		fig.savefig(output_filename)

def plot(tweets):
	
	fig = plt.figure()
	ax = plt.subplot(111)
	x_pos = np.arange(len(tweet_growth['days'].values))
	ax.bar(x_pos, tweet_growth['number_tweets'].values, align='center')
	ax.set_xticks(x_pos)
	ax.set_title('#mozfest hashtag growth')
	ax.set_ylabel("number tweets")
	ax.set_xticklabels(tweet_growth['days'].values)
	fig.savefig('airbnb_growth.png')

def processData(fname):

	texts = []
	with open(fname, 'r') as f:

		for line in f:
			try:
				tweet = json.loads(line)
				tweet['created_at']
				texts.append(tweet)
			except:
				continue

	# Create the dataframe we will use
	tweets = pd.DataFrame()
	# We want to know when a tweet was sent
	tweets['created_at'] = map(lambda tweet: time.strftime('%Y-%m-%d %H:%M:%S', time.strptime(tweet['created_at'],'%a %b %d %H:%M:%S +0000 %Y')), texts)
	# Who is the tweet owner
	tweets['user'] = map(lambda tweet: tweet['user']['screen_name'], texts)
	# How many follower this user has
	tweets['user_followers_count'] = map(lambda tweet: tweet['user']['followers_count'], texts)
	# What is the tweet's content
	tweets['text'] = map(lambda tweet: tweet['text'].encode('utf-8'), texts)
	# If available what is the language the tweet is written in
	tweets['lang'] = map(lambda tweet: tweet['lang'], texts)
	# If available, where was the tweet sent from ?
	tweets['Location'] = map(lambda tweet: tweet['place']['country'] if tweet['place'] != None else None, texts)
	# How many times this tweet was retweeted and favorited
	tweets['retweet_count'] = map(lambda tweet: tweet['retweet_count'], texts)
	tweets['favorite_count'] = map(lambda tweet: tweet['favorite_count'], texts)

	print tweets.head()

	list_of_original_tweets = [element for element in tweets['text'].values if not element.startswith('RT')]
	print list_of_original_tweets[0]

	print "Number of Original Tweets : " + str(len(list_of_original_tweets))

	list_of_retweets = [element for element in tweets['text'].values if element.startswith('RT')]
	print "Number of Retweets : " + str(len(list_of_retweets))

	return tweets

def transformation(tweet):

	df = pd.DataFrame(tweets['created_at'].value_counts(), columns=['number_tweets'])
	df['date'] = df.index
	df.head()

	days = [item.split(" ")[0] for item in df['date'].values]
	df['days'] = days
	grouped_tweets = df[['days', 'number_tweets']].groupby('days')
	tweet_growth = grouped_tweets.sum()
	tweet_growth['days']= tweet_growth.index

	tweet_growth

	plot(tweet_growth)

def wordCloud(tweet):
	text = " ".join(tweets['text'].values.astype(str))
	no_urls_no_tags = " ".join([word for word in text.split()
								if 'http' not in word
									and not word.startswith('@')
									and word != 'RT'
								])
	airbnb_mask = imread("./airbnb_mask.png", flatten=True)
	print os.environ.get("FONT_PATH", "/Library/Fonts/Verdana.ttf")
	wc = WordCloud(background_color="white", font_path=os.environ.get("FONT_PATH", "/Library/Fonts/Verdana.ttf"), stopwords=STOPWORDS, width=1800,
						  height=140, mask=airbnb_mask)
	wc.generate(no_urls_no_tags)
	plt.imshow(wc)
	plt.axis("off")
	plt.savefig('airbnb.png', dpi=300)

if __name__ == '__main__':
	dir_path = os.path.dirname(os.path.realpath(__file__))
	fname = os.path.join(dir_path, sys.argv[1])
	tweets = processData(fname)

	plot_tweets_per_category(tweets['lang'], "#airbnb by Language", 
							 "Language", 
							 "Number of Tweets", 
							 2000,
							 "output/airbnb_per_language.png")

	plot_tweets_per_category(tweets['Location'], 
							 "#airbnb by Location", 
							 "Location", 
							 "Number of Tweets", 2000,
							 "output/airbnbt_per_location.png")

	plot_tweets_per_category(tweets['user'], 
							 "#airbnb active users", 
							 "Users", 
							 "Number of Tweets", 20,
							 "output/airbnb_users.png")

	plot_distribution(tweets['retweet_count'], 
					  "#airbnb retweets distribution", "", "",
					  "output/retweets_distribution.png")

	wordCloud(tweets)