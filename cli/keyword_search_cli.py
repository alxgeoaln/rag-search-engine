#!/usr/bin/env python3

import argparse
import json

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
    
    subparsers.add_parser("build", help="build search query") 
    
    args = parser.parse_args()

    match args.command:
        case "search":
            print(f"Searching for: {args.query}")
            # format_print(
            #     find_movies_matches(data,  utilities.tokenize_text(args.query))
            # )
            query_tokens = utilities.tokenize_text(args.query)
            inverted_index.load()
            for token in query_tokens:
                docs = inverted_index.get_documents(token)
                format_print(docs)
                
        case "build":
            inverted_index.build()
            inverted_index.save()
        case _:
            parser.print_help()


if __name__ == "__main__":
    main()