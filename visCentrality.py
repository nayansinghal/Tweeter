from time import gmtime, mktime, strptime
import pandas as pd
import networkx as nx
from operator import itemgetter
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np

"""
Clean out limit messages, etc.
"""
def cleanData(data):
    print("clean Data start ...")
    for tweet in data:
        try:
            user = tweet['user']
            text = tweet['text']
        except:
            data.remove(tweet)
    print("Total text after cleaning: ",len(data))
    print("clean Data Finish ...")

    return data

def extractTweetReTweetData(data):
    #
    # Pull the data we're interested in out of the Twitter data we captured
    #
    print("extract Tweet ReTweet Data start ....")
    rows_list = []
    now = mktime(gmtime())
    for tweet in data:
        author = ""
        rtauthor = ""
        age = rtage = followers = rtfollowers = 0
    #
    # If it was a retweet, get both the original author and the retweeter, save the original author's
    # follower count and age
    #
        try:
            author = tweet['user']['screen_name']
            rtauthor = tweet['retweeted_status']['user']['screen_name']
            rtage = int(now - mktime(strptime(tweet['retweeted_status']['user']['created_at'], "%a %b %d %H:%M:%S +0000 %Y")))/(60*60*24)
            rtfollowers = tweet['retweeted_status']['user']['followers_count']
        except:
    #
    # Otherwise, just get the original author
    #
            try:
                author = tweet['user']['screen_name']
            except:
                continue
    #
    # If this was a reply, save the screen name being replied to
    #
        reply_to = ""
        if (tweet['in_reply_to_screen_name'] != None):
            reply_to = tweet['in_reply_to_screen_name']
    #
    # Calculate the age, in days, of this Twitter ID
    #
        age = int(now - mktime(strptime(tweet['user']['created_at'], "%a %b %d %H:%M:%S +0000 %Y")))/(60*60*24)
    #
    # Grab this ID's follower count and the text of the tweet
    #
        followers = tweet['user']['followers_count']
        text = tweet['text']
        dict1 = {}
    #
    # Construct a row, add it to our list
    #
        dict1.update({'author': author, 'reply_to': reply_to, 'age': age, 'followers': followers, 'retweet_of': rtauthor, 'rtfollowers': rtfollowers, 'rtage': rtage, 'text': text})
        rows_list.append(dict1)

    #
    # When we've processed all the tweets, build the DataFrame from the rows
    # we've collected
    #
    tweets = pd.DataFrame(rows_list)
    print("extract Tweet ReTweet Data end ....")
    return tweets

def createTweetReTweetGraph(data):
    print("Create Tweet Retweet graph start ...")
    tweets = extractTweetReTweetData(data)
    #
    # Create a new directed graph
    #
    graph = nx.DiGraph()
    #
    # Iterate through the rows of our dataframe
    #
    for index, row in tweets.iterrows():
    #
    # Gather the data out of the row
    #
        this_user_id = row['author'].lower()
        author = row['retweet_of'].lower()
        followers = row['followers']
        age = row['age']
        rtfollowers = row['rtfollowers']
        rtage = row['rtage']
    #
    # Is the sender of this tweet in our network?
    #
        if not this_user_id in graph:
            graph.add_node(this_user_id, attr_dict={
                    'followers': row['followers'],
                    'age': row['age'],
                })
    #
    # If this is a retweet, is the original author a node?
    #
        if author != "" and not author in graph:
            graph.add_node(author, attr_dict={
                    'followers': row['rtfollowers'],
                    'age': row['rtage'],
                })
    #
    # If this is a retweet, add an edge between the two nodes.
    #
        if author != "":
            if graph.has_edge(author, this_user_id):
                graph[author][this_user_id]['weight'] += 1
            else:
                graph.add_weighted_edges_from([(author, this_user_id, 1.0)])
                
    print("Create Tweet Retweet graph end ...")
    return graph

def plotGraph(graph, dataSorted, title, outFilename, top_k = 10, cmap=plt.cm.YlOrRd):
    print("Draw Graph start ...")
    
    plt.close()
    highest_degree = [node[0] for node in dataSorted[0:top_k]]
    sub = graph.subgraph(highest_degree)
    spring_pos = nx.spring_layout(sub, k=0.75, iterations =200)

    nodes = sub.nodes()
    degree = sub.degree()

    color = [degree[n] for n in nodes]
    d = nx.degree(sub)
    size  = [v * 300 for v in d.values()]

    nx.draw(sub, pos=spring_pos,node_color=color,with_labels=True, node_size=size, alpha=0.9, cmap=cmap)
    plt.axis('off')
    plt.savefig(outFilename + '.png', bbox_inches="tight")
    print("Draw Graph end ...")

def autolabel(ax, rects):
    """
    Attach a text label above each bar displaying its height
    """
    for rect in rects:
        height = rect.get_height()
        ax.text(rect.get_x() + rect.get_width()/2., 1.05*height,
                '%d' % int(height),
                ha='center', va='bottom')

def plotBarGraph(graph, data, title, outFilename, top_k = 10):
	
	print("Draw Bar Graph start ...")
	users = []
	values = []
	for user, value in data[0:top_k]:
	    users.append(user)
	    values.append(value)

	ind = np.arange(top_k)  # the x locations for the groups
	width = 0.65       # the width of the bars

	fig, ax = plt.subplots()
	rects = ax.bar(ind, values[0:top_k], width, color='green')

	# add some text for labels, title and axes ticks
	ax.set_ylabel('Users')
	ax.set_title(title)
	ax.set_xticks(ind + width / 2)
	ax.set_xticklabels(users)
	plt.setp(ax.get_xticklabels(), rotation= 15, fontsize=8, color='black')

	autolabel(ax, rects)

	fig.savefig(outFilename + 'Bar.png')
	print("Draw Bar Graph end ...")

def sortDrawSave(graph, degree, title, outFilename, top_k = 10):
    #TODO: use networkx variable and sort instead of using degree variable
    degree_sorted = sorted(degree.items(), key=itemgetter(1), reverse=True)
    
    f = open(outFilename + '.txt', 'w')
    for key, value in degree_sorted[0:top_k]:
        f.write(key + ' ' + str(value) + '\n')
    f.close()
    
    plotGraph(graph, degree_sorted, title, outFilename, top_k)
    plotBarGraph(graph, degree_sorted, title, outFilename, top_k)
    
def degreeCentrality(J, title, outFilename, top_k = 10):

    print("Calculate Degree Centrality start ...")
    degree = nx.degree(J)
    nx.set_node_attributes(J, 'degree', degree)
    nx.set_node_attributes(J, 'indegree', J.in_degree)
    nx.set_node_attributes(J, 'outdegree', J.out_degree)
    
    sortDrawSave(J, degree, title, outFilename)
    print("Calculate Degree Centrality end ...")

def eigenCentrality(J, title, outFilename, top_k=10):
    print("Calculating Eigen Centrality start ...")
    
    ec = nx.eigenvector_centrality(J)
    nx.set_node_attributes(J, 'eigen_cent', ec)
    sortDrawSave(J, ec, title, outFilename)
    
    print("Calculating Eigen Centrality end ...")

def betweenessCentrality(J, title, outFilename, top_k=10):
    print("Calculating Betweeness Centrality start ...")
    
    bc = nx.betweenness_centrality(J)
    nx.set_node_attributes(J, 'between_cent', bc)
    sortDrawSave(J, bc, title, outFilename)
    
    print("Calculating Betweeness Centrality end ...")