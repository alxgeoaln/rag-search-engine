import string
from nltk.stem import PorterStemmer

BM25_K1 = 1.5
BM25_B = 0.75

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

def tokenize_text(text: str) -> list[str]:
    lowerText = text.lower()
    table = str.maketrans("", "", string.punctuation)
    textWithoutPunctuation = lowerText.translate(table)
    
    splitText = remove_stop_words(
        list(
            filter(lambda x: x != " ", textWithoutPunctuation.split()) 
        )
    ) 
    
    tokens = list(
        map(
            lambda x: stemmer.stem(x),
            splitText
        )
    )
    return tokens