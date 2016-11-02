import sys
import json
import operator
import os
from pprint import pprint

def TopHashTags(fname):

	dic={}
	count=1
	with open(fname, 'r') as new:

		for line in new:
			data=json.loads(line)
	
			sum=0
			if "entities" in data:
				print data['entities']
				l=data["entities"]
				l2=l.encode('ascii','ignore')

				ht=l["hashtags"]

				ter = l2.split(" ")
				print (ter)
				for d in ht:
		
					ht3=d["text"] 
					ht2=ht3.encode('ascii','ignore')
					if ht2 in dic:
						dic[ht2]+=1
					else:
						dic.update({ht2:count})

	for ht2,count in dic.items():
		print str(ht2)+"\t"+str(count)

	sorts = sorted(dic.iteritems(), key=operator.itemgetter(1), reverse=True)

	i=0
	for k in sorts:
		i=i+1
		if (i<=10):
			print k[0]+"\t"+str(k[1])         

if __name__ == '__main__':
	dir_path = os.path.dirname(os.path.realpath(__file__))
	fname = os.path.join(dir_path, sys.argv[1])
	TopHashTags(fname)
	
