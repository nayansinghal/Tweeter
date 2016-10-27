from gensim import corpora, models
import pyLDAvis.gensim
import matplotlib.pyplot as plt

corpus = corpora.MmCorpus('data/corpus.mm')
dictionary = corpora.Dictionary.load('data/dictionary.dict')

lda = models.LdaModel.load('data/document.lda')
followers_data =  pyLDAvis.gensim.prepare(lda, corpus, dictionary)
pyLDAvis.save_html(followers_data, 'hello.html')