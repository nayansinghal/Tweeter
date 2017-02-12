from vaderSentiment.vaderSentiment import sentiment as vaderSentiment
import unicodedata
import heapq as heap

def saveFile(hp, outFilename):
    f = open(outFilename, 'w')
    while hp:
        f.write(str(heap.heappop(hp)[1]) + '\n')
    f.close()

def sentimentalAnalysis(data, outFilename):
    print('Sentimental Analysis start ...')
    neg = 0
    pos = 0
    neutral = 0
    hpos = []
    hneg = []

    count = -1
    for text in data:
        if text:
            vs = vaderSentiment(text)
            x = list(vs.iteritems())
            if float(x[1][1]) >= float(x[0][1]) and float(x[1][1]) >= float(x[2][1]):
                neutral +=1
            elif float(x[0][1]) >= float(x[1][1]) and float(x[0][1]) >= float(x[2][1]):
                neg +=1
            else:
                pos +=1
            heap.heappush(hneg, (-x[0][1], text))
            heap.heappush(hpos, (-x[2][1], text))

    print(neg, neutral, pos)
    saveFile(hpos, outFilename + 'pos.txt')
    saveFile(hpos, outFilename + 'neg.txt')