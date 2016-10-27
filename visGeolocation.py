###################

# python visGeolocation.py "file_path"

################
import json
import os
import sys

# Tweets are stored in "fname"
# Generate geo_data.json containing tweet's location latitude and longitude 
def convertToGeo(fname):

	with open(fname, 'r') as f:
		geo_data = {
			"type": "FeatureCollection",
			"features": []
		}

		for line in f:
			try:
				tweet = json.loads(line)
				if tweet['coordinates']:
					geo_json_feature = {
						"type": "Feature",
						"geometry": tweet['coordinates'],
						"properties": {
							"text": tweet['text'],
							"created_at": tweet['created_at']
						}
					}
					geo_data['features'].append(geo_json_feature)
				
			except:
				continue
 
	# Save geo data
	with open('output/geo_data.json', 'w') as fout:
		fout.write(json.dumps(geo_data, indent=4))

if __name__ == '__main__':

	dir_path = os.path.dirname(os.path.realpath(__file__))
	fname = os.path.join(dir_path, sys.argv[1])

	convertToGeo(fname)
