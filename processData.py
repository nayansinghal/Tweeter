###################

# python processData.py "filepath"

################

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
import langid
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

def filter_lang(lang, document):

	doclang = langid.classify(document)
	return doclang[0]
	##return [documents[k] for k in range(len(documents)) if doclang[k][0] == lang

def preprocess(s, lowercase=False):

	tokens = tokenize(s)
	if lowercase:
		tokens = [token if emoticon_re.search(token) else token.lower() for token in tokens]
	return tokens

# Remove stop words
stoplist_tw=['amp','get','got','hey','hmm','hoo','hop','iep','let','ooo','par',
			'pdt','pln','pst','wha','yep','yer','yet','aest','didn','nzdt','via',
			'one','com','new','like','great','make','top','awesome','best',
			'good','wow','yes','say','yay','would','thanks','thank','going',
			'new','use','should','could','best','really','see','want','nice',
			'while','know', 'rt', 'via', 'it', 'u', 'c', 'co', 'http', 'w', 'r', '1', '2', '3',
			'gt', 'v', 'It', 'e', 'k', 'gg']

punctuation = list(string.punctuation)
stop = set(stopwords.words('english') + stoplist_tw) 
exclude = set(string.punctuation)
lemma = WordNetLemmatizer()


def clean(text):
	text=re.sub('[^a-z0-9 ]',' ',text.lower())
	text=re.sub('  +',' ', text).strip()
	stop_free = [i for i in text.split(' ') if i not in stop]
	normalized = [lemma.lemmatize(word) for word in stop_free]
	return ' '.join(normalized)

def processData(fname):

	texts = []
	with open(fname, 'r') as f:

		for line in f:
			try:
				tweet = json.loads(line)
				if filter_lang('en', tweet['text']) == "en":
					texts.append(clean(tweet['text']).split())
			except:
				continue

	token_frequency = defaultdict(int)
	# count all token
	for doc in texts:
		for token in doc:
			token_frequency[token] += 1

	# keep words that occur more than once
	texts = [ [token for token in doc if token_frequency[token] > 1] for doc in texts ]
	
	# Creating the term dictionary of our courpus, where every unique term is assigned an index.
	dictionary = corpora.Dictionary(texts)
	dictionary.save('output/dictionary.dict')

	bow_corpus = [dictionary.doc2bow(doc) for doc in texts]
	corpora.MmCorpus.serialize('output/corpus.mm', bow_corpus)

	## apply LDA
	lda = gensim.models.ldamodel.LdaModel(bow_corpus, num_topics=3, id2word = dictionary, passes=20)
	lda_corpus = lda[bow_corpus]

	lda.save('output/document.lda')
	print("lda saved in %s " % 'output/document.lda')

	return lda_corpus

def clusttering(lda_corpus):

	matrix = [[x[1] for x in row] for row in lda_corpus]
	matrix=np.array(matrix)
	print matrix

	print('LDA matrix shape:', matrix.shape)

	km = KMeans(n_clusters=4, init='k-means++', max_iter=100, n_init=4, verbose=False, random_state=10)
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

