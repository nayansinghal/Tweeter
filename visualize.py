from gensim import corpora, models
import pyLDAvis.gensim
import matplotlib.pyplot as plt

corpus = corpora.MmCorpus('output/corpus.mm')
dictionary = corpora.Dictionary.load('output/dictionary.dict')

lda = models.LdaModel.load('output/document.lda')
followers_data =  pyLDAvis.gensim.prepare(lda, corpus, dictionary)
pyLDAvis.save_html(followers_data, 'output/LdaModel.html')