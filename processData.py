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
from collections import Counter
from collections import defaultdict
from nltk import bigrams
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem.wordnet import WordNetLemmatizer
from tweepy import Stream
from tweepy import OAuthHandler
from tweepy.streaming import StreamListener
from gensim import corpora

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

	terms_stop = []
	with open(fname, 'r') as f:
		count_all = Counter()

		for line in f:
			try:
				tweet = json.loads(line)
			except:
				continue
			# Create a list with all the terms
			terms_stop.append(clean(tweet['text']).split())

	# Creating the term dictionary of our courpus, where every unique term is assigned an index.
	dictionary = corpora.Dictionary(terms_stop)

	doc_term_matrix = [dictionary.doc2bow(doc) for doc in terms_stop]

	## apply LDA
	Lda = gensim.models.ldamodel.LdaModel
	ldamodel = Lda(doc_term_matrix, num_topics=3, id2word = dictionary, passes=50)

	lda_corpus = ldamodel[doc_term_matrix]

if __name__ == '__main__':
	dir_path = os.path.dirname(os.path.realpath(__file__))
	fname = os.path.join(dir_path, sys.argv[1])
	data = processData(fname)