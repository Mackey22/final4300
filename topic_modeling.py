from nltk.corpus import stopwords
from nltk.stem.wordnet import WordNetLemmatizer
import string
from gensim import corpora
from gensim.models.ldamodel import LdaModel as Lda
import time
import json
# import sklearn.feature_extraction.text.CountVectorizer as CV


def preprocess(corpus, fullclean=False):
    if fullclean:
        stop = set(stopwords.words('english'))
        exclude = set(string.punctuation)
        lemma = WordNetLemmatizer()

        def clean(doc):
            stop_free = " ".join([i for i in doc.lower().split() if i not in stop])
            punc_free = ''.join(ch for ch in stop_free if ch not in exclude)
            normalized = " ".join(lemma.lemmatize(word) for word in punc_free.split())
            return normalized

        corpus = [clean(doc) for doc in corpus]

    doc_clean = [doc.split() for doc in corpus]
    return doc_clean


def return_topic_model(corpus, doc_term_matrix=None, dictionary=None):
    # # Creating the term dictionary of our courpus, where every unique term is assigned an index.
    dictionary = corpora.Dictionary(corpus)

    # # Converting list of documents (corpus) into Document Term Matrix using dictionary prepared above.
    doc_term_matrix = [dictionary.doc2bow(doc) for doc in corpus]

    pruningstart = time.time()
    dictionary.filter_extremes(no_below=5, no_above=0.8, keep_n=10000)
    vals = dictionary.values()
    doc_term_matrix = [dictionary.doc2bow(filter(lambda x: x in vals, doc)) for doc in corpus]
    print "Pruning to 10000 features took", time.time() - pruningstart, "Seconds"

    # Running and Training LDA model on the document term matrix.
    ldamodel = Lda(doc_term_matrix, num_topics=15, id2word=dictionary, passes=5)
    print ldamodel
    return ldamodel


def reduce_review_size():
    """Reduce review size so we can play with topics without worrying about load time."""
    start = time.time()
    with open('jsons/reviews.json') as data_file:
        reviews = json.load(data_file)
    print "opening reviews took", time.time() - start, "seconds"

    keys = reviews.keys()
    new_dict = {}
    for i in range(1000):
        new_dict[keys[i]] = reviews[keys[i]]
    with open('jsons/small_reviews.json', 'w') as fp:
        json.dump(new_dict, fp)


def train_model(size="small"):
    """Mess around with topic modeling."""
    reviews = {}

    start = time.time()
    if size == "small":
        with open('jsons/small_reviews.json') as data_file:
            reviews = json.load(data_file)
    else:
        with open('jsons/reviews.json') as data_file:
            reviews = json.load(data_file)
    print "opening reviews took", time.time() - start, "seconds"

    prepreprocessstart = time.time()
    keys = reviews.keys()
    corpus = [reviews[key]["reviews"] for key in keys]
    print "Pre-Pre-processing took", time.time() - prepreprocessstart, "seconds"

    preprocessstart = time.time()
    # doc_term_matrix, dictionary = preprocess(corpus, fullclean=True)
    corpus = preprocess(corpus, fullclean=True)
    print "Preprocessing took", time.time() - preprocessstart, "seconds"

    ldastart = time.time()
    model = return_topic_model(corpus)
    model.save("ldamodel")
    print "lda took", time.time() - ldastart, "seconds"
    print "Total process took", time.time() - start, "seconds"


def model_play(fname):
    start = time.time()
    ldamodel = Lda.load(fname)
    print "Model loaded in", time.time() - start, "seconds"

    for i in range(25):
        print ldamodel.print_topic(i)


if __name__ == "__main__":
    # train_model()
    # model_play("ldamodel")
    reduce_review_size()
