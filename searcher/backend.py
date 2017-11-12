import json
from pandas import read_csv
from gensim.summarization import summarize
import os

from .indexer import DocumentsIndex
from .engine import Engine

MERGED_FILES_DIR = 'MERGED_FILES'
SOURCE_FILES_DIR = '001'
JSON_FILES_DIR = "MERGED_JSONS"


class Backend:
    def __init__(self, meta_data_file, index_file):
        index = DocumentsIndex()
        index.load_index_from_file(index_file)
        index.fill_doc_len()
        self.indexer = index
        self.engine = Engine(index)

        column_names = ['post_id', 'type', 'title']
        self.meta_data = read_csv(meta_data_file, sep='\t', names=column_names)

    def process_query(self, query):
        query.lower().split()
        preprocessed_query = self.indexer.run_stemmer(query)
        found = self.engine.process_query(preprocessed_query)
        found_filtered = [(file, relevance) for file, relevance in found[:20]
                          if os.path.isfile(os.path.join(MERGED_FILES_DIR, file[len(SOURCE_FILES_DIR) + 1:]))]
        found_filtered = found_filtered[:10]
        all_results = []
        for file, relevance in found_filtered:
            results = {}
            doc_id = file[len(SOURCE_FILES_DIR) + 1:]
            doc_type, title = self.get_meta_data(doc_id)

            results["id"] = doc_id
            results["relevance"] = relevance
            results["type"] = doc_type
            results["title"] = title
            results["summary"] = "PLEASE CALL Backend.summarize(id, SOURCE_FILES_DIR)"
            sentiment, keywords, categories, locations = self.get_info_from_json(doc_id)
            results['sentiment'] = sentiment
            results['keywords'] = keywords
            results['categories'] = categories
            results['locations'] = locations
            all_results.append(results)
        global_stats = {}
        global_stats['docs_found'] = len(found)
        global_stats['sentiment'] = float(0.0)
        global_stats['keywords'] = []
        global_stats['locations'] = []
        global_stats['categories'] = []
        for result in all_results:
            for location in result['locations']:
                global_stats['locations'].append(location[0])
            global_stats['keywords'].append((result['keywords'][0][0], float(result['keywords'][0][1]) * float(result['relevance'])))
            global_stats['sentiment'] += float(result['sentiment']) * float(result['relevance'])
            for category in result['categories']:
                global_stats['categories'].append(category[0])
        return global_stats, all_results

    @staticmethod
    def summarize(post_id, dir_texts):
        with open(os.path.join(dir_texts, post_id)) as infile:
            data = infile.read()
        result = []
        if len(data.split('.')) > 1:
            print("ratio = ", float(500) / len(data))
            summary = summarize(data, ratio=float(500) / len(data), split=True)
            print("summary = ",  summary)

            seen = set()
            result = []
            for item in summary:
                if item not in seen:
                    seen.add(item)
                    result.append(item)

        if not result:
            result = data
        result = ' '.join(result)
        return result

    @staticmethod
    def get_info_from_json(doc_id):
        with open(os.path.join(JSON_FILES_DIR, doc_id + '.json')) as fin:
            data = fin.read()
        watson_data = json.loads(data)
        sentiment = float(watson_data['sentiment']['document']['score'])
        keywords = []
        for json_keyword in watson_data['keywords']:
            keywords.append((json_keyword['text'], float(json_keyword['relevance'])))
        categories = []
        for json_category in watson_data['categories']:
            categories.append((json_category['label'], float(json_category['score'])))
        locations = []
        for json_entities in watson_data['entities']:
            if json_entities['type'] != 'Location':
                continue
            locations.append((json_entities['text'], float(json_entities['relevance'])))
        return sentiment, keywords, categories, locations

    def get_meta_data(self, post_id):
        obj_type = self.meta_data[self.meta_data['post_id'] == post_id]["type"].to_string(index=False)
        title = self.meta_data[self.meta_data['post_id'] == post_id]["title"].to_string(index=False)
        return obj_type, title
