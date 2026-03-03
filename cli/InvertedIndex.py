import json
import pickle
import os

import utilities


class InvertedIndex():
    index: dict[str, list[int]] = {}
    docmap: dict = {}
    
    def __add_document(self, doc_id, text):
        tokens = utilities.tokenize_text(text)
        for token in tokens:
            if token in self.index:
                self.index[token].append(doc_id)
            else:
                self.index[token] = [doc_id]
    
    def get_documents(self, term: str):
        result = []
        lowercase_term = term.lower()
        
        ids = []
        if lowercase_term in self.index:
            ids = self.index[lowercase_term]
        
        for id in ids:
            result.append(self.docmap[id])
            
        return result
    
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
                    
    