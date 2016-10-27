import tweepy
import time
import argparse
import string
import json
import os
import sys
import re
import operator 
import gensim
import pprint
import unicodedata
import matplotlib.pyplot as plt
import numpy as np
from collections import Counter
from collections import defaultdict
from gensim import corpora
from nltk import bigrams
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem.wordnet import WordNetLemmatizer
from sklearn import metrics
from sklearn.cluster import KMeans
from tweepy import Stream
from tweepy import OAuthHandler
from tweepy.streaming import StreamListener

emoticons_str = r"""
	(?:
		[:=;] # Eyes
		[oO\-]? # Nose (optional)
		[D\)\]\(\]/\\OpP] # Mouth
	)"""
 
regex_str = [
	emoticons_str,
	r'<[^>]+>', # HTML tags
	r'(?:@[\w_]+)', # @-mentions
	r"(?:\#+[\w_]+[\w\'_\-]*[\w_]+)", # hash-tags
	r'http[s]?://(?:[a-z]|[0-9]|[$-_@.&amp;+]|[!*\(\),]|(?:%[0-9a-f][0-9a-f]))+', # URLs
 
	r'(?:(?:\d+,?)+(?:\.?\d+)?)', # numbers
	r"(?:[a-z][a-z'\-_]+[a-z])", # words with - and '
	r'(?:[\w_]+)', # other words
	r'(?:\S)' # anything else
]
	
tokens_re = re.compile(r'('+'|'.join(regex_str)+')', re.VERBOSE | re.IGNORECASE)
emoticon_re = re.compile(r'^'+emoticons_str+'$', re.VERBOSE | re.IGNORECASE)
 
def tokenize(s):
	return tokens_re.findall(s)
 
def preprocess(s, lowercase=False):

	print s
	tokens = tokenize(s)
	if lowercase:
		tokens = [token if emoticon_re.search(token) else token.lower() for token in tokens]
	return tokens

stop = set(stopwords.words('english'))
exclude = set(string.punctuation)
lemma = WordNetLemmatizer()

def clean(s):

	stop_free = " ".join([i for i in s.lower().split() if i not in stop])
	punc_free = ''.join(ch for ch in stop_free if ch not in exclude)
	normalized = " ".join(lemma.lemmatize(word) for word in punc_free.split())
	return normalized

def processData(fname):

	punctuation = list(string.punctuation)
	stop = stopwords.words('english') + punctuation + ['rt', 'via', 'RT']

	texts = []
	with open(fname, 'r') as f:
		count_all = Counter()

		for line in f:
			try:
				tweet = json.loads(line)
			except:
				continue
			# Create a list with all the terms
			texts.append(clean(tweet['text']).split())

	# Creating the term dictionary of our courpus, where every unique term is assigned an index.
	dictionary = corpora.Dictionary(texts)
	dictionary.save('data/dictionary.dict')

	bow_corpus = [dictionary.doc2bow(doc) for doc in texts]
	corpora.MmCorpus.serialize('data/corpus.mm', bow_corpus)

	## apply LDA
	lda = gensim.models.ldamodel.LdaModel(bow_corpus, num_topics=3, id2word = dictionary, passes=20)
	lda_corpus = lda[bow_corpus]

	lda.save('data/document.lda')
	print("lda saved in %s " % 'data/document.lda')

	print list(lda_corpus)
	return lda_corpus

def clusttering(lda_corpus):

	matrix = [[x[1] for x in row] for row in lda_corpus]
	matrix=np.array(matrix)
	print matrix

	print('LDA matrix shape:', matrix.shape)

	km = KMeans(n_clusters=3, init='k-means++', max_iter=100, n_init=4, verbose=False, random_state=10)
	km.fit(matrix)
	print(km.labels_)

	plt.title('Documents in the LDA space')
	plt.xlabel('Dimension / Topic 1')
	plt.ylabel('Dimension / Topic 2')
	plt.scatter(km.cluster_centers_[:,0], km.cluster_centers_[:,1], marker='x', s=169, linewidths=3, color='g', zorder=10)
	plt.scatter(matrix[:,0], matrix[:,1])
	unique_labels = set(km.labels_)
	colors = plt.cm.Spectral(np.linspace(0, 1, len(unique_labels)))
	xy = matrix[km.labels_==0]
	plt.scatter(xy[:,0], xy[:,1], color='r')
	plt.show()

	silhouette_coefficient = metrics.silhouette_score(matrix, km.labels_, sample_size=1000)
	print('Silhouette Coefficient:', silhouette_coefficient)
	
if __name__ == '__main__':
	dir_path = os.path.dirname(os.path.realpath(__file__))
	fname = os.path.join(dir_path, sys.argv[1])
	lda_corpus = processData(fname)
	clusttering(lda_corpus)

