import json
import os
import matplotlib as mpl
import matplotlib.pyplot as plt

def saveFile(labels, sizes, values, outFilename):
    
    # check dir exists and save fig
    dir = os.path.dirname(outFilename)
    if not os.path.exists(dir):
        os.makedirs(dir)
        
    f = open(outFilename + '.txt', 'w')
    for i in range(0, len(sizes)):
        f.write(labels[i].encode('utf-8') + " " + str(sizes[i]) + " " + str(values[i]) + "\n")
    f.close()

"""
Create & Save Donut Chart
TODO: label for small sizes intersect
"""
def plotDonutDist(labels, sizes, title, outFilename):
    
    fig, ax = plt.subplots()
    ax.pie(sizes, labels=labels,
        autopct='%1.1f%%', shadow=True)
        
    #draw a circle at the center of pie to make it look like a donut
    centre_circle = plt.Circle((0,0),0.75,color='black', fc='white',linewidth=1.25)
    fig.gca().add_artist(centre_circle)

    # Set aspect ratio to be equal so that pie is drawn as a circle.
    ax.axis('equal')
    ax.legend(loc='lower right',fontsize=7)
    ax.set_title(title)  
    
    # check dir exists and save fig
    dir = os.path.dirname(outFilename)
    if not os.path.exists(dir):
        os.makedirs(dir)
    fig.savefig(outFilename)

"""
Generatng Donut plot for different information extracted
"""
def langDist(data, topk, title, outFilename):
    print("create donut chart: " + title)
    top = (data.value_counts()[0:topk]/ data.value_counts().sum())*100
    
    labels = [];sizes = []; values = [];
    
    for label, size in top.iteritems():
        labels.append(label)
        sizes.append(size)
        values.append((size * data.value_counts().sum())/100)
    
    labels.append("Other")
    sizes.append(100 - ((data.value_counts()[0:5]/ data.value_counts().sum())*100).sum())
    values.append(data.value_counts().sum() - data.value_counts()[0:5].sum())
    saveFile(labels, sizes, values, outFilename)
    
    plotDonutDist(labels, sizes, title, outFilename + '.png')
    print("File saved ...")

def extractGeoLocation(data, outFilename):

	geo_data = {
	    "type": "FeatureCollection",
	    "features": []
	}

	for tweet in data:
	    try:
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
	with open(outFilename, 'w') as fout:
	    fout.write(json.dumps(geo_data, indent=4))