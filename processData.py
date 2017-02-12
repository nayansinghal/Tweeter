import argparse
import json
import pandas as pd
import time
import visLocAndLangDist as visLocAndLangDist
import visActiveUsers as visActiveUsers
import visTweetRetweetDist as visTweetRetweetDist
import visHyperlink as visHyperlink
import visCentrality as visCentrality
import visMentionGraph as visMentionGraph
import visWordCloud as wc
import visWordCollocation as visWordCollocation
import visTopicModelling as visTopicModelling
import visSentiment as visSentiment

"""
Open file, retrieve data and append it to data
"""
def processData(fname):
    print("Data Processing start ....");
    data = []
    with open(fname, 'r') as f:
        for line in f:
            try:
                tweet = json.loads(line)
                data.append(tweet)
            except:
                continue
    print("Total Data Length: ",len(data))
    print("Data Processing End ...")
    return data

"""
Crate dataFrame from data, extract
created_at, user, text, lang, location, retweet_count, favorite_count
"""
def createDataFrame(data):
    
    # Create the dataframe we will use
    print("DataFrame Creation Start ...")
    
    tweets = pd.DataFrame()
    # We want to know when a tweet was sent
    tweets['created_at'] = map(lambda tweet: time.strftime('%Y-%m-%d %H:%M:%S', time.strptime(tweet['created_at'],'%a %b %d %H:%M:%S +0000 %Y')) if "created_at" in tweet and tweet['created_at'] != None else None, data)
    # Who is the tweet owner
    tweets['user'] = map(lambda tweet: tweet['user']['screen_name'] if 'user' in tweet and tweet['user'] != None else None, data)
    # How many follower this user has
    # What is the tweet's content
    tweets['text'] = map(lambda tweet: tweet['text'].encode('utf-8')  if 'text' in tweet else None, data)
    # If available what is the language the tweet is written in
    tweets['lang'] = map(lambda tweet: tweet['lang'] if 'lang' in tweet else None, data)
    # If available, where was the tweet sent from ?
    tweets['Location'] = map(lambda tweet: tweet['place']['country'] if "place" in tweet and tweet['place'] != None else None, data)
    # How many times this tweet was retweeted and favorited
    tweets['retweet_count'] = map(lambda tweet: tweet['retweet_count'] if "retweet_count" in tweet else 0, data)
    tweets['favorite_count'] = map(lambda tweet: tweet['favorite_count'] if "favorite_count" in tweet else 0, data)
    
    print("DataFrame Creation End ...")
    
    return tweets

if __name__ == '__main__':
	fname = 'data/stream_BuyBlack.json'
	data = processData(fname)
	tweets = createDataFrame(data)

	visLocAndLangDist.langDist(tweets['lang'], 10, "Language Distribution", "output/langDist")
	visLocAndLangDist.langDist(tweets['Location'], 10, "Location Distribution", "output/location")
	visLocAndLangDist.extractGeoLocation(data, 'output/geoData.json')

	visActiveUsers.plot_tweets_per_category(tweets['user'], 
							 "Active Users", 
							 "Users", 
							 "Number of Tweets", 10,
							 "output/users", "#9E004B", 20)

	visTweetRetweetDist.plotReTweetDist(tweets['retweet_count'], 
					  "Retweets distribution", "retweet", "Frequency Distribution",
					  50, "output/Retweets_distribution.png")
	
	visTweetRetweetDist.tweetGrowth(tweets['created_at'], "output/Tweet_growth.png")

	visHyperlink.extractHyperLinks(tweets['text'], "output/hyperlink")

	data = visCentrality.cleanData(data)
	J = visCentrality.createTweetReTweetGraph(data)
	visCentrality.degreeCentrality(J, 'Degree Centrality','output/degreeCentrality', 10)
	visCentrality.eigenCentrality(J, 'Eigen Centrality','output/EigenCentrality', 10)
	visCentrality.betweenessCentrality(J, 'Betweeness Centrality','output/BetweenessCentrality', 10)

	mentionGraph = visMentionGraph.createMentionGraph(tweets['text'], tweets['user'], 'output/mentionGraph')
	visCentrality.degreeCentrality(mentionGraph, 'Mention Degree Centrality','output/mentionDegreeCentrality', 10)
	
	wc.wordCloud(tweets['text'], 'data/insecure-hbo.jpg', 'output/wordCloud.png')
	visWordCollocation.createCollocationGraph(tweets['text'], 'output/collocationGraph.gexf')
	visTopicModelling.ldaModelling(tweets['text'], 'output/topic')
	visSentiment.sentimentalAnalysis(tweets['text'], 'output/')
