import json
import pickle
import os
import collections
import math

import utilities


class InvertedIndex():
    def __init__(self):
        self.index: dict[str, list[int]] = {}
        self.docmap: dict = {}
        self.term_frequencies: dict[int, collections.Counter] = {}
    
    def __add_document(self, doc_id, text):
        tokens = utilities.tokenize_text(text)
        for token in tokens:
            if token in self.index:
                self.index[token].append(doc_id)
            else:
                self.index[token] = [doc_id]
            
         
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
        
        return self.term_frequencies[doc_id].get(tokens.pop())
    
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

    def load(self):
        cache_dir = os.path.isdir("cache")
        
        if not cache_dir:
            raise FileNotFoundError("Cache doesn't exist")
        
        index_pkl = os.path.isfile("cache/index.pkl")
        docmap_pkl = os.path.isfile("cache/docmap.pkl")
        
        if not index_pkl or not docmap_pkl:
            raise FileNotFoundError("index or docmap doesn't exist")
        
        with open("cache/index.pkl", "rb") as file:
            self.index = pickle.load(file)
            
        with open("cache/docmap.pkl", "rb") as file:
            self.docmap = pickle.load(file)
            
        with open("cache/term_frequencies.pkl", "rb") as file:
            self.term_frequencies = pickle.load(file)
                    
    