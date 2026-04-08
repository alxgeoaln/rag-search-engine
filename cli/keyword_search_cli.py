#!/usr/bin/env python3

import argparse

import utilities
import InvertedIndex

def has_matching_token(query_tokens: list[str], title_tokens: list[str]):
    for query_token in query_tokens:
            for title_token in title_tokens:
                if query_token in title_token:
                    return True
                
    return False
        
def find_movies_matches(data: dict, query: list[str]) -> list:
    result = []
    
    for item in data['movies']:
        if has_matching_token(query, utilities.tokenize_text(item['title'])):
            result.append(item)
        
        if len(result) == 5:
            break

    return result

def format_print(items: list):
    for item in items:
        print(f"{item['id']}. {item['title']}")

def main() -> None:
    inverted_index = InvertedIndex.InvertedIndex()
    
    parser = argparse.ArgumentParser(description="Keyword Search CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    search_parser = subparsers.add_parser("search", help="Search movies using BM25")
    search_parser.add_argument("query", type=str, help="Search query")
    
    tf_parser = subparsers.add_parser("tf", help="Build search query") 
    tf_parser.add_argument("id", help="Document id")
    tf_parser.add_argument("term", help="Term to search")
    
    idf_parser = subparsers.add_parser("idf", help="Get Inverse Document Frequency")
    idf_parser.add_argument("term", help="Term to search")
    
    tfidf_parser = subparsers.add_parser("tfidf", help="get tfidf")
    tfidf_parser.add_argument("id", help="Doc id")
    tfidf_parser.add_argument("term", help="Term to search")
    
    bm25_idf_parser = subparsers.add_parser("bm25idf", help="Get BM25 IDF score for a given term")
    bm25_idf_parser.add_argument("term", type=str, help="Term to get BM25 IDF score for")
    
    bm25_tf_parser = subparsers.add_parser(
  "bm25tf", help="Get BM25 TF score for a given document ID and term"
)
    bm25_tf_parser.add_argument("doc_id", type=int, help="Document ID")
    bm25_tf_parser.add_argument("term", type=str, help="Term to get BM25 TF score for")
    bm25_tf_parser.add_argument("k1", type=float, nargs='?', default=utilities.BM25_K1, help="Tunable BM25 K1 parameter")
    bm25_tf_parser.add_argument("b", type=float, nargs='?', default=utilities.BM25_B, help="Tunable BM25 b parameter")
    
    bm25search_parser = subparsers.add_parser("bm25search", help="Search movies using full BM25 scoring")
    bm25search_parser.add_argument("query", type=str, help="Search query")
    
    subparsers.add_parser("build", help="build search query")
    
    args = parser.parse_args()

    match args.command:
        case "search":
            print(f"Searching for: {args.query}")
            query_tokens = utilities.tokenize_text(args.query)
            inverted_index.load()
            for token in query_tokens:
                docs = inverted_index.get_documents(token)
                format_print(docs)
                
        case "tf":
            print(f"Getting TF for: {args.id}, {args.term}")
            inverted_index.load()
            result = inverted_index.get_tf(int(args.id), args.term)
            print(result)
            
        case "idf":
            print(f"Getting IDF for: {args.term}")
            inverted_index.load()
            result = inverted_index.get_idf(args.term)
            print(f"Inverse document frequency of '{args.term}': {result:.2f}")
            
        case "tfidf":
            inverted_index.load()
            score = 0

            idf = inverted_index.get_idf(args.term)
            tf = inverted_index.get_tf(int(args.id), args.term)
            score += tf * idf
            print(f"TF-IDF score of '{args.term}' in document '{args.id}': {score:.2f}")
            
        case "bm25idf":
            inverted_index.load()
            bm25idf = inverted_index.get_bm25_idf(args.term)
            print(f"BM25 IDF score of '{args.term}': {bm25idf:.2f}")
            
        case "bm25tf":
            inverted_index.load()
            bm25tf = inverted_index.get_bm25_tf(args.doc_id, args.term, args.k1)
            print(f"BM25 TF score of '{args.term}' in document '{args.doc_id}': {bm25tf:.2f}")
            
        case "bm25search":
            inverted_index.load()
            res = inverted_index.bm25_search(args.query, 5)
            print(res)
        case "build":
            print("Building...")
            try:
                inverted_index.build()
                inverted_index.save()
                print("build ok")
                # print(f"Total tokens: {sum(inverted_index.doc_lengths.values())}")
                # print(f"Avg doc length: {inverted_index._InvertedIndex__get_avg_doc_length()}")
                # print(f"Doc 1 length: {inverted_index.doc_lengths[1]}")
                # print(f"TF of 'anbuselvan' in doc 1: {inverted_index.get_tf(1, 'anbuselvan')}")
                # print(f"Num docs: {len(inverted_index.doc_lengths)}")
                # print(utilities.tokenize_text("The police are having a great time with her"))
                # print(utilities.tokenize_text("a movie about a young boy and his dog"))
            except:
                print("build failed")
        case _:
            parser.print_help()


if __name__ == "__main__":
    main()