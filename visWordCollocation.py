from nltk import bigrams
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.tokenize import RegexpTokenizer
from nltk import FreqDist
from nltk.corpus import brown
from nltk import BigramCollocationFinder
import networkx as nx

def extractTokens(data):
    #divide to words
    print('Extract Tokens')
    words = []
    tokenizer = RegexpTokenizer(r'\w+')
    for text in data:
        if text:
            temp = tokenizer.tokenize(text)
            for word in temp:
                words.append(word)
    
    return words

def generateMostCommonWords():
    print('Generate Common Words')
    fdist = FreqDist(brown.words())
    mostcommon = fdist.most_common(100)
    mclist = []

    for i in range(len(mostcommon)):
        mclist.append(mostcommon[i][0])
        
    return mclist

def removeCommonWords(data):
    print('Remove Common Words')
    mcList = generateMostCommonWords()
    stoplist_tw=['amp','get','got','hey','hmm','hoo','hop','iep','let','ooo','par',
            'pdt','pln','pst','wha','yep','yer','yet','aest','didn','nzdt','via',
            'one','com','new','like','great','make','top','awesome','best',
            'good','wow','yes','say','yay','would','thanks','thank','going',
            'new','use','should','could','best','really','see','want','nice',
            'while','know', 'rt', 'via', 'it', 'u', 'c', 'co', 'http', 'w', 'r', '1', '2', '3',
            'gt', 'v', 'It', 'e', 'k', 'gg','www', 'n', 's', 'twitter', 'ly', 'For', 'pic', 't',
             '\xc2', '\xe2', 'An', 'an', 'https', 'Https'
            ]
    stop = set(stopwords.words('english') + stoplist_tw) 
    words = [w for w in data if w not in mcList and w not in stop]
    
    return words

def createCollocationGraph(data, title):
    
    print('Create Collocation Graph')
    
    words = extractTokens(data)
    words = removeCommonWords(words)

    #find word pairs
    finder = BigramCollocationFinder.from_words(words, window_size = 5)
    pairs = sorted(finder.ngram_fd.items(), key=lambda t: (-t[1], t[0]))
    
    collocation = nx.DiGraph()
    for key, value in pairs:
        left = key[0].lower()
        right = key[1].lower()
        if left not in collocation:
            collocation.add_node(left)
        if right not in collocation:
            collocation.add_node(right)
        if collocation.has_edge(left, right):
            collocation[left][right]['weight'] += value
        else:
            collocation.add_weighted_edges_from([(left, right, value)])
            
    nx.write_gexf(collocation, title)