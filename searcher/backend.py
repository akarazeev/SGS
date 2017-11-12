import json
from pandas import read_csv
from gensim.summarization import summarize
import os


class Backend:
    def __init__(self, database_file, index_file):
        self.database_file = database_file
        self.index_file = index_file

        column_names = ['post_id', 'regulation', 'name']
        self.data = read_csv(database_file, sep='\t', names=column_names)

    def match_title(self, post_id):
        self.type = self.data[self.data['post_id'] == post_id]["tqype"]
        self.title = self.data[self.data['post_id'] == post_id]["title"]

    def summarize(self, post_id, dir_texts):
        with open(os.path.join(dir_texts,post_id)) as infile:
            data = infile.read()

            summary = set(summarize(data, split=True))
            if not summary:
                summary = data


    def out_json(self, output_file):
        with open(output_file, 'w') as outfile:
            json.dump(data, outfile)

    def build_cloud(self):





