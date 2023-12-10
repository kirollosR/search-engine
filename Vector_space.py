from Preprocessing import load_data
from prettytable import PrettyTable as pt
import pandas as pd
import math
import numpy as np

document_of_terms = load_data()


def all_words():
    # from main import document_of_terms
    all_words = []
    for doc in document_of_terms:
        for word in doc:
            all_words.append(word)
    return all_words


def get_term_freq(doc):
    words_found = dict.fromkeys(all_words(), 0)
    for word in doc:
        words_found[word] += 1
    return words_found


term_freq = pd.DataFrame(get_term_freq(document_of_terms[0]).values(),
                         index=get_term_freq(document_of_terms[0]).keys())

for i in range(1, len(document_of_terms)):
    term_freq[i] = get_term_freq(document_of_terms[i]).values()

term_freq.columns = ['doc' + str(i) for i in range(1, 11)]


def create_table(df, title, index='Term'):
    # Convert the columns and index to a list for PrettyTable
    columns = list(df.columns)
    index_column = [index]  # Assuming the index column has a name; change it accordingly
    index_values = list(df.index)

    # Create a PrettyTable instance with column names from the DataFrame
    table = pt(index_column + columns)

    # Add a title to the PrettyTable
    table.title = title

    # Loop through each row in the DataFrame and add it to the PrettyTable
    for index, row in df.iterrows():
        table.add_row([index] + row.tolist())

    # Print the PrettyTable
    print(table)


def tf_table():
    create_table(term_freq, 'TF')


def get_weighted_term_freq(x):
    if x > 0:
        return math.log10(x) + 1
    return 0


def weighted_tf_table():
    for i in range(1, len(document_of_terms) + 1):
        term_freq['doc' + str(i)] = term_freq['doc' + str(i)].apply(get_weighted_term_freq)

    create_table(term_freq, 'Weighted TF')


idf = pd.DataFrame(columns=['freq', 'idf'])
def idf_table():


    for i in range(len(term_freq)):
        frequency = term_freq.iloc[i].values.sum()

        idf.loc[i, 'freq'] = frequency

        idf.loc[i, 'idf'] = round(math.log10(10 / (float(frequency))), 3)

    idf.index = term_freq.index

    create_table(idf, 'IDF')


tfIdf = pd.DataFrame()
def tf_idf_table():
    global tfIdf
    tfIdf = term_freq.multiply(idf['idf'], axis=0)

    create_table(tfIdf, 'TF.IDF')


document_length = pd.DataFrame()
def document_length_table():
    global document_length
    def get_docs_length(col):
        return round(np.sqrt(tfIdf[col].apply(lambda x: x ** 2).sum()), 3)


    for column in tfIdf.columns:
        document_length.loc[0, column + '_len'] = get_docs_length(column)

    create_table(document_length, 'Document Length', 'Index')

normalized_term_freq_idf = pd.DataFrame()
def normalized_tf_idf_table():
    global tfIdf
    global document_length
    global normalized_term_freq_idf

    def get_normalized(col, x):
        try:
            return round(x / document_length[col + '_len'].values[0], 3)
        except:
            return 0

    for column in tfIdf.columns:
        normalized_term_freq_idf[column] = tfIdf[column].apply(lambda x: get_normalized(column, x))

    create_table(normalized_term_freq_idf, "Normalized TF.IDF", 'Index')
