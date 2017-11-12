import json
from wordcloud import WordCloud
import matplotlib.pyplot as plt


def readjs(filename):
    """
    Read json from jsons/.
    """
    with open('jsons/' + filename, 'r') as f:
        datajs = json.load(f)
    return datajs


def get_keywords(datajs, topn=5):
    """
    Return keywords for document `filename`.
    """
    keywords = sorted(datajs['keywords'], key=lambda x: x['relevance'], reverse=True)
    return keywords[:topn]


def make_wordcloud(keywords, imname='tmp.png'):
    """
    Save wordcloud for `keywords`.
    keywords - list of tuples [(word, freq), ...]
    """
    wordcloud = WordCloud(background_color='white',
                          max_font_size=40,
                          random_state=42).generate_from_frequencies(dict(keywords))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis("off")
    plt.savefig(imname, bbox_inches='tight')


to_cut = ['food and drink', 'law, govt and politics',
          'health and fitness', 'business and industrial']


def subcat(category, to_cut=to_cut):
    category = category.split('/')
    if category[1] in to_cut and len(category) > 3:
        return category[2]
    else:
        return category[1]


def category(entry):
    long_category = sorted(entry['categories'], key=lambda x: x[1], reverse=True)[0][0]
    subcat(long_category)
    return long_category
