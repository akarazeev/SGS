from .util import get_all_files
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
import numpy as np
import pickle
import string


class DocumentsIndex:
    def __init__(self):
        self.word_to_doc = {}
        self.doc_len = {}
        self._stemmer = PorterStemmer()

    def add_directory_to_index(self, data_directory, checkpoints=True):
        i = 0
        for file in get_all_files(data_directory):
            self.add_file_to_index(file)
            i += 1
            if i % 1000 == 0:
                if checkpoints:
                    self.save_index_to_file("checkpoint" + str(i))
                print("Processed 1000 more files")

    def add_file_to_index(self, file):
        all_words = self._preprocess_file(file)
        words_count = {}
        for word in all_words:
            if word in words_count:
                words_count[word] += 1
            else:
                words_count[word] = 1
        assert file not in self.word_to_doc
        for word, count in words_count.items():
            if word not in self.word_to_doc:
                self.word_to_doc[word] = []
            self.word_to_doc[word].append((file, count))

    def save_index_to_file(self, file):
        with open(file, "wb") as fout:
            pickle.dump(self.word_to_doc, fout, pickle.HIGHEST_PROTOCOL)

    def load_index_from_file(self, file):
        with open(file, "rb") as fin:
            self.word_to_doc = pickle.load(fin)

    def get_avg_doc_len(self):
        return np.mean(list(self.doc_len.values()))

    def fill_doc_len(self):
        for docs in self.word_to_doc.values():
            for doc, _ in docs:
                if doc not in self.doc_len:
                    self.doc_len[doc] = 0
                self.doc_len[doc] += 1

    def _preprocess_file(self, file):
        all_words = []
        with open(file, 'r') as fin:
            for line in fin:
                tokens = line.lower().split()
                words = DocumentsIndex._remove_stopwords_and_punctuation(tokens)
                words = self.run_stemmer(words)
                all_words.extend(words)
        return all_words

    @staticmethod
    def _remove_stopwords_and_punctuation(words_list):
        return [word for word in words_list
                if word not in stopwords.words('english') and word not in string.punctuation]

    def run_stemmer(self, words_list):
        return [self._stemmer.stem(word) for word in words_list]
