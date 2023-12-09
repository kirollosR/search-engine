import os
from nltk.tokenize import word_tokenize
from natsort import natsorted
from nltk.stem import PorterStemmer

def preprocessing(doc):
    token_docs = word_tokenize(doc)

    prepared_doc = []
    for term in token_docs:
        stemmed = stemming(term)
        prepared_doc.append(stemmed)


    return prepared_doc

def stemming(word):
    porter = PorterStemmer()
    stemmed_words = porter.stem(word)
    return stemmed_words

def load_data():
    files_name = natsorted(os.listdir('files'))

    document_of_terms = []
    for files in files_name:
        with open(f'files\{files}', 'r') as f:
            document = f.read()
        document_of_terms.append(preprocessing(document))

    return document_of_terms

def print_data(document_of_terms):
    print('Terms after tokenization and stemming')
    print(document_of_terms)
    for doc in document_of_terms:
        print(doc)
    print('-' * 80 + '\n')