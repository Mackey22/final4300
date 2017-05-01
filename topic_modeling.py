import time
import json
import string
import numpy as np

from scipy import sparse, io
from sklearn.preprocessing import normalize
from nltk.corpus import stopwords
from nltk.stem.wordnet import WordNetLemmatizer
from gensim import corpora
from gensim.models.ldamodel import LdaModel as Lda


MODEL_PATH = "ldamodel"


def sort_dict_by_val(d):
    """Get a list of a dict's keys ordered by descending values."""
    return sorted(d, key=d.__getitem__, reverse=True)


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


def return_topic_model(corpus, numpasses, numtopics, doc_term_matrix=None, dictionary=None):
    if doc_term_matrix is None and dictionary is None:
        # # Creating the term dictionary of our courpus, where every unique term is assigned an index.
        dictionary = corpora.Dictionary(corpus)

        # # Converting list of documents (corpus) into Document Term Matrix using dictionary prepared above.
        doc_term_matrix = np.array([dictionary.doc2bow(doc) for doc in corpus])

        pruningstart = time.time()
        dictionary.filter_extremes(no_below=5, no_above=0.8, keep_n=10000)
        vals = dictionary.values()
        doc_term_matrix = [dictionary.doc2bow(filter(lambda x: x in vals, doc)) for doc in corpus]
        print "[INFO] Pruning to 10000 features took", time.time() - pruningstart, "Seconds"
        with open("matrix.json", "w") as df:
            json.dump(doc_term_matrix, df)
        dictionary.save("topics_dt_mtx/dict")

    # Running and Training LDA model on the document term matrix.
    ldamodel = Lda(doc_term_matrix, num_topics=numtopics, id2word=dictionary, passes=numpasses)
    return ldamodel


def reduce_review_size():
    """Reduce review size so we can play with topics without worrying about load time."""
    start = time.time()
    with open('jsons/reviews.json') as data_file:
        reviews = json.load(data_file)
    print "[INFO] opening reviews took", time.time() - start, "seconds"

    keys = reviews.keys()
    new_dict = {}
    for i in range(300):
        new_dict[keys[i]] = reviews[keys[i]]
    with open('jsons/small_reviews.json', 'w') as fp:
        json.dump(new_dict, fp)


def see_restaurants(n=200):
    with open("jsons/pruned_reviews.json") as df:
        reviews = json.load(df)
    keys = reviews.keys()
    for i in range(n):
        print "[INFO]", reviews[keys[i]]['data']['name']


def train_model(corpus, numpasses=30, num_topics=30, size="medium", load_mtx=True):
    """Mess around with topic modeling."""
    print "\n[INFO] Making", numpasses, "passes"
    print "[INFO] Making", num_topics, "topics"
    start = time.time()

    if load_mtx:
        print "[INFO] Loading doc-term-matrix"

        with open("matrix.json") as df:
            doc_term_matrix = json.load(df)
        dictionary = corpora.Dictionary().load("topics_dt_mtx/dict")

        ldastart = time.time()
        model = return_topic_model(None, numpasses, num_topics, doc_term_matrix, dictionary)
    else:
        print "[INFO] Computing doc-term-matrix"
        preprocessstart = time.time()
        corpus = preprocess(corpus, fullclean=True)
        print "[INFO] Preprocessing took", time.time() - preprocessstart, "seconds"

        ldastart = time.time()
        model = return_topic_model(corpus, numpasses, num_topics)

    model.save(MODEL_PATH)
    print "[INFO] lda took", time.time() - ldastart, "seconds"
    print "[INFO] Total process took", time.time() - start, "seconds"
    return model


def model_play(fname):
    """Extract insights from trained model."""
    start = time.time()
    ldamodel = Lda.load(fname)
    print "[INFO] Model loaded in", time.time() - start, "seconds"

    for i in range(ldamodel.num_topics):
        print "[INFO]",ldamodel.print_topic(i)


def get_matrices():
    start = time.time()
    with open("matrix.json") as df:
        doc_term_matrix = json.load(df)
    dictionary = corpora.Dictionary().load("topics_dt_mtx/large_dict")
    ldamodel = Lda.load(MODEL_PATH)
    loaded = time.time()
    print "Doc-Term Matrix loaded in", loaded - start, "seconds"

    doc_topic_mtx = ldamodel[doc_term_matrix]
    topic_word_mtx = ldamodel.print_topics()
    array = []
    for i in range(len(doc_topic_mtx)):
        mp = {}
        for topic_id, topic_score in doc_topic_mtx[i]:
            mp[topic_id] = topic_score
        array.append(mp)

    with open("doc_topic_mtx.json", "w") as df:
        json.dump(array, df)
    with open("topic_word_mtx.json", "w") as df:
        json.dump(topic_word_mtx, df)

    for i in topic_word_mtx:
        print i
    print "Doc-Topic and Topic-Word Matrices loaded in", time.time() - loaded, "seconds"

    return array, dictionary, ldamodel


def make_big_dt_matrix():
    train_model(numpasses=1, num_topics=2, size="large", load_mtx=False)


def convert_to_sparse():
    doc_topic_mtx, dictionary, ldamodel = get_matrices()
    num_cols = ldamodel.num_topics
    num_rows = len(doc_topic_mtx)

    t = time.time()
    sparse_matrix = sparse.csr_matrix((num_rows, num_cols), dtype=float)
    for doc_idx, row in enumerate(doc_topic_mtx):
        if doc_idx % 1000 == 0:
            print "Converted", doc_idx, "docs in", time.time() - t, "seconds"
        for topic_idx, score in row:
            sparse_matrix[doc_idx, topic_idx] = score

    t = time.time()
    sparse_matrix = normalize(sparse_matrix, norm="l2")
    print "Matrix normalized in", time.time() - t, "seconds"
    io.mmwrite("topicmodel/doc_topic_small.mtx", sparse_matrix)
    return sparse_matrix


def make_corpus(unique_ids):
    with open('jsons/reviews.json') as data_file:
        reviews = json.load(data_file)
    corpus = [reviews[key]["reviews"] for key in unique_ids]
    return corpus


def do_everything(unique_ids=["--9e1ONYQuAa-CB_Rrw7Tw", "pX3TM1r3PTgUdfUTAjk44w", "rnvsL0oFZpzpO61GXqBF6g", "FuNMqkKUGzDnX4XJcJee4Q", "Bmv3nHS2nfjzhkDQMsLAWQ", "lGmXgLQklCW0laI5Gdxopw", "cbjb-iJaZ7XydkCrFmuSjQ", "AKMvsVr_9meoSmawkEBe4g", "OaM2Bjeo2Ftt84ruTrzPNQ", "-sX7hDKR_bdBVQxuOaO5dA", "7gHdVSAz_Dm1wS1ZImJSiQ", "WfDB6grqF9-1bOAP505Lqg", "ePkouyI6uFc9ifEzvxD4jw", "xsdRrNJuNumvrwoQ2Tt8tQ"]):
    with open("topics_dt_mtx/unique_ids.json", "w") as df:
        json.dump(unique_ids, df)

    corpus = make_corpus(unique_ids)
    model = train_model(corpus, numpasses=40, num_topics=40, load_mtx=False)
    doc_topic_mtx, _, _ = get_matrices()
    return doc_topic_mtx


def get_similar_topics(idx1, idx2, topicid_to_label, doc_topic_mtx):
    id_to_score1 = doc_topic_mtx[idx1]
    id_to_score2 = doc_topic_mtx[idx2]

    topics = []
    for k1 in sort_dict_by_val(id_to_score1):
        if k1 in id_to_score2 and k1 in topicid_to_label:
            topics.append(topicid_to_label[k1])
    return topics


if __name__ == "__main__":
    do_everything()
    # convert_to_sparse()
    # train_model(num_topics=15)
    # model_play(MODEL_PATH)
    # train_model(numpasses=40, num_topics=40, load_mtx=False, size="small")
    # model_play(MODEL_PATH)
    # train_model(num_topics=25)
    # model_play(MODEL_PATH)
    # train_model(num_topics=30)
    # model_play(MODEL_PATH)
    # train_model(num_topics=35)
    # model_play(MODEL_PATH)
    # train_model(num_topics=40)
    # model_play(MODEL_PATH)
    # reduce_review_size()
    # see_restaurants()
    # get_matrices()
