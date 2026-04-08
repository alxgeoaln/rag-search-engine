import json
import pickle
import os
import collections
import math

import utilities


class InvertedIndex():
    def __init__(self):
        self.index: dict[str, set[int]] = {}
        self.docmap: dict = {}
        self.term_frequencies: dict[int, collections.Counter] = {}
        self.doc_lengths = {}
    
    def __add_document(self, doc_id, text):
        tokens = utilities.tokenize_text(text)
        for token in tokens:
            if token in self.index:
                self.index[token].add(doc_id)
            else:
                self.index[token] = {doc_id}
            
        doc_len = len(tokens)
        self.doc_lengths[doc_id] = doc_len
         
        if doc_id in self.term_frequencies:
            self.term_frequencies[doc_id].update(tokens)
        else:
            self.term_frequencies[doc_id] = collections.Counter(tokens)
    
    def get_documents(self, term: str):
        result = []
        lowercase_term = term.lower()
        
        ids = []
        if lowercase_term in self.index:
            ids = self.index[lowercase_term]
        
        for id in ids:
            result.append(self.docmap[id])
            
        return result
    
    def get_tf(self, doc_id: int, term: str):
        tokens = utilities.tokenize_text(term)
        
        if len(tokens) != 1:
            raise ValueError("no more than one term")
        
        val =  self.term_frequencies[doc_id].get(tokens.pop())
        
        return val if val else 0
    
    # inverted document freq
    def get_idf(self, term: str):
        tokens = utilities.tokenize_text(term)
        
        if len(tokens) != 1:
            raise ValueError("no more than one term")
        
        token = tokens[0]
        doc_count = len(self.docmap)
        term_doc_count = len(self.index[token])
        
        idf = math.log((doc_count + 1) / (term_doc_count + 1))
        return idf
        
    def get_bm25_idf(self, term: str) -> float:
        tokens = utilities.tokenize_text(term)
        
        if len(tokens) != 1:
            raise ValueError("no more than one term")
        
        token = tokens[0]
        N = len(self.docmap)
        df = len(self.index[token])
        
        # print(f"N={N}, df={df}")
        
        IDF = math.log((N - df + 0.5) / (df + 0.5) + 1)
        
        return IDF
     
    def get_bm25_tf(self, doc_id, term, k1=utilities.BM25_K1, b=utilities.BM25_B) -> float:
        tf = self.get_tf(doc_id, term)
        doc_length = self.doc_lengths[doc_id]
        avg_doc_length = self.__get_avg_doc_length()
        # Length normalization factor
        length_norm = 1 - b + b * (doc_length / avg_doc_length)

        # Apply to term frequency
        tf_component = (tf * (k1 + 1)) / (tf + k1 * length_norm)
        
        return tf_component
     
    def bm25(self, doc_id, term):
        bm25_tf = self.get_bm25_tf(doc_id, term)
        bm25_idf = self.get_bm25_idf(term)
        
        return bm25_tf * bm25_idf
    
    def bm25_search(self, query, limit):
        tokens = utilities.tokenize_text(query)
        
        scores = {}
        
        for token in tokens:
            if token in self.index:
               doc_ids = self.index[token]
               
               for doc_id in doc_ids:
                    scores[doc_id] = (scores.get(doc_id, 0) + self.bm25(doc_id, token))
                    
        output = dict(sorted(scores.items(), key=lambda item: item[1], reverse=True))
        # print(output)
        
        result = ""
        for i, key in enumerate(output.keys()):
            if i == limit:
                break
            # print(key)
            res = f"{i + 1}. ({key}) {self.docmap[key]['title']} - Score: {output[key]:.2f}"
            if i == 0:
                result += res
            else:
                result += f"\n {res}"
                
        return result
            
     
    def __get_avg_doc_length(self) -> float:
        count = 0
        docs_len = 0
        for doc_len in self.doc_lengths.values():
            docs_len += doc_len
            count += 1
            
        if count == 0:
            return 0.0
        else :
            return docs_len / count
        
    def build(self):
        with open("data/movies.json", "r") as file:
            data = json.load(file)

        for movie in data['movies']:
            self.docmap[movie['id']] = movie
            text = f"{movie['title']} {movie['description']}"
            self.__add_document(movie['id'], text)
    
    
    def save(self):
        cache_dir = os.path.isdir("cache")
        if not cache_dir:
            os.mkdir("cache")
        
        with open("cache/index.pkl", "wb") as file:
            pickle.dump(self.index, file)
            
        with open("cache/docmap.pkl", "wb") as file:
            pickle.dump(self.docmap, file)
            
        with open("cache/term_frequencies.pkl", "wb") as file:
            pickle.dump(self.term_frequencies, file)
        
        with open("cache/doc_lengths.pkl", "wb") as file:
            pickle.dump(self.doc_lengths, file)

    def load(self):
        cache_dir = os.path.isdir("cache")
        
        if not cache_dir:
            raise FileNotFoundError("Cache doesn't exist")
        
        index_pkl = os.path.isfile("cache/index.pkl")
        docmap_pkl = os.path.isfile("cache/docmap.pkl")
        docs_length_pkl = os.path.isfile("cache/doc_lengths.pkl")
        
        if not index_pkl or not docmap_pkl or not docs_length_pkl:
            raise FileNotFoundError("index or docmap doesn't exist")
        
        with open("cache/index.pkl", "rb") as file:
            self.index = pickle.load(file)
            
        with open("cache/docmap.pkl", "rb") as file:
            self.docmap = pickle.load(file)
            
        with open("cache/term_frequencies.pkl", "rb") as file:
            self.term_frequencies = pickle.load(file)
            
        with open("cache/doc_lengths.pkl", "rb") as file:
            self.doc_lengths = pickle.load(file)
            

                    
    