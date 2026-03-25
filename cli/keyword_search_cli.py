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
            print(result)
            
        case "tfidf":
            inverted_index.load()
            score = 0
            
            print(args.id, args.term)

            idf = inverted_index.get_idf(args.term)
            tf = inverted_index.get_tf(int(args.id), args.term)
            score += tf * idf
            print(f"TF-IDF score of '{args.term}' in document '{args.id}': {score:.2f}")
                
        case "build":
            print("Building...")
            inverted_index.build()
            inverted_index.save()
        case _:
            parser.print_help()


if __name__ == "__main__":
    main()