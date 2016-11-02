from vaderSentiment.vaderSentiment import sentiment as vaderSentiment
import sys
import json
from pprint import pprint
import os
import unicodedata
import pandas as pd
import heapq as heap

def main(fname): 
	
	new=open(fname)
	neg = 0
	pos = 0
	neutral = 0
	hpos = []
	hneg = []
	count = 0
	for line in new:
		data=json.loads(line)
		count += 1
		if "text" in data:
			l=data["text"].encode("utf-8")
			vs = vaderSentiment(l)
			x =  list(vs.iteritems())
			print x
			heap.heappush(hneg, (-x[0][1], l))
			heap.heappush(hpos, (-x[2][1], l))
			'''
			if float(x[1][1]) >= float(x[0][1]) and float(x[1][1]) >= float(x[2][1]):
				neutral +=1
			elif float(x[0][1]) >= float(x[1][1]) and float(x[0][1]) >= float(x[2][1]):
				neg +=1
			else:
				pos +=1
			'''

	top_k = 50

	for i in range(0, top_k):
		print heap.heappop(hneg)

	print "----------------------------"

	for i in range(0, top_k):
		print heap.heappop(hpos)
	#print pos, neg, neutral

					  
if __name__ == '__main__':
	dir_path = os.path.dirname(os.path.realpath(__file__))
	fname = os.path.join(dir_path, sys.argv[1])
	main(fname)

