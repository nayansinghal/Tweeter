import re

def saveFile(data, outFilename):
    f = open(outFilename + '.txt', 'w')
    for value in data:
        f.write(value + "\n")
    f.close()

def extractLink(text):
    regex = r'https?://[^\s<>"]+|www\.[^\s<>"]+'
    match = re.search(regex, text)
    if match:
        return match.group()
    return ''

# TODO: remove blank hyperlinks
# Extract all the hyperlinks from the text
def extractHyperLinks(data, outFilename):
    hyperlink = []
    for tweet in data:
        if tweet != None:  
            link = extractLink(tweet)
            if link != None:
                hyperlink.append(link)
    saveFile(hyperlink, outFilename)