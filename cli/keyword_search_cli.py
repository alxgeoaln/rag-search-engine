#!/usr/bin/env python3

import argparse
import json
import string
from nltk.stem import PorterStemmer

stemmer = PorterStemmer()

def remove_stop_words(tokens: list[str]) -> list[str]:
    with open("data/stop_words.txt", "r") as file:
        data = file.read().splitlines()
    
    for item in data:
        if item in tokens:
            tokens = list(
                filter(
                    lambda x: x != item,
                    tokens
                )
            )
            
    return tokens

def format_text(text: str) -> list[str]:
    lowerText = text.lower()
    table = str.maketrans("", "", string.punctuation)
    textWithoutPunctuation = lowerText.translate(table)
    
    splitText = remove_stop_words(
        list(
            filter(lambda x: x != " ", textWithoutPunctuation.split(" ")) 
        )
    ) 
    
    tokens = list(
        map(
            lambda x: stemmer.stem(x),
            splitText
        )
    )
    return tokens

def has_matching_token(query_tokens: list[str], title_tokens: list[str]):
    for query_token in query_tokens:
            for title_token in title_tokens:
                if query_token in title_token:
                    return True
                
    return False
        
def find_movies_matches(data: dict, query: list[str]) -> list:
    result = []
    
    for item in data['movies']:
        if has_matching_token(query, format_text(item['title'])):
            result.append(item)
        
        if len(result) == 5:
            break

    return result

def format_print(items: list):
    for index, item in enumerate(items):
        print(f"{index + 1}. {item['title']}")

def main() -> None:
    parser = argparse.ArgumentParser(description="Keyword Search CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    search_parser = subparsers.add_parser("search", help="Search movies using BM25")
    search_parser.add_argument("query", type=str, help="Search query")

    args = parser.parse_args()
    
    with open("data/movies.json", "r") as file:
        data = json.load(file)
        

    match args.command:
        case "search":
            print(f"Searching for: {args.query}")
            format_print(
                find_movies_matches(data, format_text(args.query))
            )
            pass
        case _:
            parser.print_help()


if __name__ == "__main__":
    main()