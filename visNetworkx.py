import json
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
from matplotlib import rcParams
from mpltools import style
from datetime import datetime
import seaborn as sns
import time
import os
import numpy as np
import sys
import re
import networkx as nx

def processData(fname):

	texts = []
	count  = 0
	with open(fname, 'r') as f:

		for line in f:
			try:
				count += 1
				tweet = json.loads(line)
				texts.append(tweet)
			except:
				continue

	print count
	print len(texts)
	# Create the dataframe we will use
	tweets = pd.DataFrame()
	# We want to know when a tweet was sent
	tweets['created_at'] = map(lambda tweet: time.strftime('%Y-%m-%d %H:%M:%S', time.strptime(tweet['created_at'],'%a %b %d %H:%M:%S +0000 %Y')), texts)
	# Who is the tweet owner
	tweets['user'] = map(lambda tweet: tweet['user']['screen_name'] if tweet['user'] != None else None, texts)
	# How many follower this user has
	#tweets['user_followers_count'] = map(lambda tweet: tweet['user']['followers_count'] if tweet['user'] != None and tweet['user']['followers_count'] != None else None, texts)
	# What is the tweet's content
	tweets['text'] = map(lambda tweet: tweet['text'].encode('utf-8'), texts)
	# If available what is the language the tweet is written in
	tweets['lang'] = map(lambda tweet: tweet['lang'], texts)
	# If available, where was the tweet sent from ?
	tweets['Location'] = map(lambda tweet: tweet['place']['country'] if "place" in tweet and tweet['place'] != None else None, texts)
	# How many times this tweet was retweeted and favorited
	tweets['retweet_count'] = map(lambda tweet: tweet['retweet_count'] if "retweet_count" in tweet else 0, texts)
	tweets['favorite_count'] = map(lambda tweet: tweet['favorite_count'] if "favorite_count" in tweet else 0, texts)

	print tweets.head()

	return tweets

if __name__ == '__main__':
	dir_path = os.path.dirname(os.path.realpath(__file__))
	fname = os.path.join(dir_path, sys.argv[1])
	tweets = processData(fname)

	ls = tweets['user'].value_counts()[:20]
	user = list(ls.iteritems())[0][0]
	tweet = list(ls.iteritems())[0][1]

	G=nx.Graph()
	G.position={}
	G.population={}

	count = 0
	for fl in list(ls.iteritems()):
		name = fl[0]
		value = fl[1]
		G.add_node(name)
		G.population[name] = int(value)
		G.position[name] = int(value)
		count += 100

	H=nx.Graph()
	for v in G:
		H.add_node(v)
	for (u,v,d) in G.edges(data=True):
		if d['weight'] < 300:
			H.add_edge(u,v)

	node_color=[G.population[v] for v in H]
	positions = nx.spring_layout( G )
	nx.draw(H, positions,
			 node_size=[G.population[v] for v in H],
			 node_color=node_color,
			 with_labels=False)
	plt.savefig( "g.png" )

	'''
	G.add_node(user)
	G.position[user]=(100,200)
	G.add_edge(user, tweet, weight = int(tweet))
	nx.draw(G)
	plt.draw()
	plt.savefig( "g.png" )
	'''