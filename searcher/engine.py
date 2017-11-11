import numpy as np


class Engine:
    def __init__(self, indexer):
        self.indexer = indexer
        self.avg_doc_len = self.indexer.get_avg_doc_len()

    @staticmethod
    def _score_bm25(TF, IDF, doc_len, avg_doc_len, k1=2.0, b=0.75):
        """
        :param TF: term frequency
        :param IDF: inversed document frequency
        :param doc_len: length of current document
        :param avg_doc_len: average length of documents
        :return: BM25 score for word from query
        """
        def compute_K():
            return k1 * ((1 - b) + b * (float(doc_len)/float(avg_doc_len)))

        K = compute_K()

        frac = ((k1 + 1) * TF) / (TF + K)
        return IDF * frac

    def idf(self, word):
        """
        :param word: str
        :return: float
        """
        n = len(self.indexer.word_to_doc[word])
        return np.log((len(self.indexer.doc_len) - n + 0.5) / (n + 0.5))

    def score_doc(self, query):
        """
        :param query: str
        :return scores: list
        """
        preprocessed_query = self.indexer.run_stemmer(query)
        scores = {}

        for word in preprocessed_query:
            if word not in self.indexer.word_to_doc:
                continue
            for document, word_tf in self.indexer.word_to_doc[word]:
                doc_len = self.indexer.doc_len[document]
                word_idf = self.idf(word)

                if document not in scores:
                    scores[document] = float(0)
                scores[document] += self._score_bm25(word_tf, word_idf, doc_len, self.avg_doc_len)
        return scores

    def process_query(self, query):
        """
        Return (documents  `query`.

        :param query: str
        :return entries: list of tuples
        """
        scored = list(self.score_doc(query).items())
        scored.sort(key=lambda t: -t[1])
        return [(doc, score) for doc, score in scored if score > 0.0]


if __name__ == '__main__':
    raise RuntimeError
