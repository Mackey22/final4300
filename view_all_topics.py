from gensim.models.ldamodel import LdaModel as Lda
from gensim import corpora

ldamodel = Lda.load("ldamodel")
dictionary = corpora.Dictionary().load("topics_dt_mtx/dict")

for i in range(ldamodel.num_topics):
	print map(lambda (id, score): dictionary[id], ldamodel.get_topic_terms(i))
