from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
from scipy.misc import imread
import os
import matplotlib.pyplot as plt

def wordCloud(tweets, inpFilename, outFilename):
    text = " ".join(tweets.values.astype(str))
    no_urls_no_tags = " ".join([word for word in text.split()
                                if 'http' not in word
                                    and not word.startswith('@')
                                    and word != 'RT'
                                ])
    airbnb_mask = imread(inpFilename, flatten=True)
    print os.environ.get("FONT_PATH", "/Library/Fonts/Verdana.ttf")
    wc = WordCloud(background_color="white", font_path=os.environ.get("FONT_PATH", "/Library/Fonts/Verdana.ttf"), stopwords=STOPWORDS, width=1800,
                          height=140, mask=airbnb_mask)
    wc.generate(no_urls_no_tags)
    plt.imshow(wc)
    plt.axis("off")
    plt.savefig(outFilename, dpi=300)