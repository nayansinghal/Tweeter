import matplotlib as mpl
import matplotlib.pyplot as plt

def saveIterDataToFile(data, outFilename):
    f = open(outFilename + '.txt', 'w')
    for label, size in data.iteritems():
        f.write(str(label) + " " + str(size) + "\n")
    f.close()

# General plotting function for the different information extracted
def plot_tweets_per_category(data, title, x_title, y_title, top_n=5, outFilename="plot.png", color = "green", rotation = 45):
    """
    :param category: Category plotted, can be tweets users, tweets language, tweets country etc ..
    :param title: Title of the plot
    :param x_title: List of the items in x
    :param y_title: Title of the variable plotted
    :return: a plot that we can save as pdf or png instead of displaying to the screen
    """
    tweets_by_cat = data.value_counts()
    saveIterDataToFile(tweets_by_cat[:top_n], outFilename)
    fig, ax = plt.subplots()
    ax.tick_params(axis='x')
    ax.tick_params(axis='y')
    ax.set_xlabel(x_title)
    ax.set_ylabel(y_title)
    ax.set_title(title)
    tweets_by_cat[:top_n].plot(ax=ax, kind='bar', color = color)
    plt.setp(ax.get_xticklabels(), rotation= rotation, fontsize=10)
    fig.savefig(outFilename + '.png')
    fig.show()