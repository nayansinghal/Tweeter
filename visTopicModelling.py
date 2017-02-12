import operator 
import gensim
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
from gensim import corpora, models
import pyLDAvis.gensim
import re
import string

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
            'gt', 'v', 'It', 'e', 'k', 'gg','www', 'n']

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

#http://nbviewer.jupyter.org/github/bmabey/pyLDAvis/blob/master/notebooks/Gensim%20Newsgroup.ipynb
#https://www.youtube.com/watch?v=BuMu-bdoVrU

def ldaModelling(data, title):
    ldaTexts = []
    for text in data:
        if text:
            ldaTexts.append(clean(text).split())
            
    token_frequency = defaultdict(int)
    
    # count all token
    for doc in ldaTexts:
        for token in doc:
            token_frequency[token] += 1

    # keep words that occur more than once
    cleanTexts = [ [token for token in doc if token_frequency[token] > 1] for doc in ldaTexts ]

    # Creating the term dictionary of our courpus, where every unique term is assigned an index.
    dictionary = corpora.Dictionary(cleanTexts)
    bow_corpus = [dictionary.doc2bow(doc) for doc in cleanTexts]
    
    ## apply LDA
    lda = gensim.models.ldamodel.LdaModel(bow_corpus, num_topics=5, id2word = dictionary, passes=20)
    
    topic_data =  pyLDAvis.gensim.prepare(lda, bow_corpus, dictionary)
    pyLDAvis.save_html(topic_data, title + '.html')