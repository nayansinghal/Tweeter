import seaborn as sns
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import math
import pandas as pd

def plotReTweetDist(category, title, x_title, y_title, top_k = 100, output_filename="plot.png"):
    """
    :param category: Category plotted, can be users, language, country etc ..
    :param title: Title of the plot
    :param x_title: List of the items in x
    :param y_title: Title of the variable plotted
    :return: a plot that we can save as pdf or png instead of displaying to the screen
    """
    print("Plot ReTweet Distribution Start ...")
    fig, ax = plt.subplots()
    ax.tick_params(axis='x')
    ax.tick_params(axis='y')
    ax.set_xlabel(x_title)
    ax.set_ylabel(y_title)
    ax.set_title(title)
    sns.distplot(category.values[:top_k],hist=True, color='g');
    fig.savefig(output_filename)
    
    print("Plot ReTweet Distribution End ...")

def plotTweetGrowth(category, title, outFilename, rotation = 90):

    length = len(category['days'].values)
    fig = plt.figure()
    ax = plt.subplot(111)
    x_pos = np.arange(length)
    width = 1.2/1.5
    bars = ax.bar(x_pos, category['created_at'].values, align='center', width = width, color = 'green')
    ax.set_xticks(x_pos)
    bin = math.floor(length/10.0)
    plt.xticks(np.arange(min(x_pos), max(x_pos)+1, bin))
    ax.set_title(title)
    ax.set_ylabel("Number of Tweets")
    plt.setp(ax.get_xticklabels(), rotation= rotation, fontsize=9)
    plt.xlim(0, length-0.5)
    dates = []
    dates.append(0)
    count = 0
    for date in category['days'].values:
        count += 1
        if math.fmod(count,bin) == 0:
            dates.append(date)
            count = 0
    ax.set_xticklabels(dates)
    fig.savefig(outFilename)

def tweetGrowth(data, outFilename):
    
    df= pd.DataFrame(data.value_counts())
    df['date'] = df.index
    days = [item.split(" ")[0] for item in df['date'].values]
    df['days'] = days
    grouped_tweets = df[['days', 'created_at']].groupby('days')
    tweet_growth = grouped_tweets.sum()
    tweet_growth['days']= tweet_growth.index
    
    plotTweetGrowth(tweet_growth, "Tweet Growth", outFilename, 45)