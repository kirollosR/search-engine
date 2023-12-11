from Preprocessing import preprocessing
from Vector_space import normalized_term_freq_idf, idf, create_table
import math
import numpy as np
import pandas as pd
from prettytable import PrettyTable as pt
import re

operators = ["AND", "OR", "NOT"]

def positional_index_query(query, positional_index):
    list = [[] for i in range(10)]
    for term in preprocessing(query):
        if term in positional_index.keys():
            for key in positional_index[term][1].keys():
                if list[key] != []:

                    if list[key][-1] == positional_index[term][1][key][0] - 1:
                        list[key].append(positional_index[term][1][key][0])
                else:
                    list[key].append(positional_index[term][1][key][0])
    positions = []
    for pos, list in enumerate(list, start=1):
        if len(list) == len(preprocessing(query)):
            positions.append('doc' + str(pos))
    return positions


def get_w_tf(x):
    try:
        return math.log10(x) + 1
    except:
        return 0


def product_query(q, query):
    product = normalized_term_freq_idf.multiply(query['w_tf'], axis=0)

    product2 = product.multiply(query['normalized'], axis=0)
    scores = {}
    for col in product2.columns:
        if 0 in product2[col].loc[preprocessing(q)].values:
            pass
        else:
            scores[col] = product2[col].sum()
    product_result = product2[list(scores.keys())].loc[preprocessing(q)].round(3)
    return product_result, scores


def check_words_in_index(dataframe, word_list):
    # Get the index of the DataFrame
    index_words = dataframe.index.tolist()

    # Check if all words in the list are present in the index
    return all(word in index_words for word in word_list)


def insert_query(q):
    query = pd.DataFrame(index=normalized_term_freq_idf.index)
    result = [elem1 for elem1 in preprocessing(q) if elem1 not in operators]
    print(result)
    found_in_index = check_words_in_index(query, result)

    if found_in_index:
        query['tf'] = [1 if x in preprocessing(q) else 0 for x in list(normalized_term_freq_idf.index)]
        query['w_tf'] = query['tf'].apply(lambda x: get_w_tf(x))

        # Use loc to set values in the original DataFrame
        query.loc[:, 'idf'] = idf['idf'] * query['w_tf']
        query.loc[:, 'tf_idf'] = query['w_tf'] * query['idf']

        # Use loc to set values in the original DataFrame
        query['normalized'] = (query['idf'] / np.sqrt((query['idf'] ** 2).sum())).astype(float).round(3)

        create_table(query.loc[preprocessing(q)], 'Query Details')

        product_result, scores = product_query(q, query)

        create_table(product_result, 'Product (query*matched doc)')

        summary_table = product_result.sum().reset_index()
        summary_table.columns = ['Term', 'Sum']
        create_table(summary_table, 'Product Sum', '')

        ql = pt(['Query Length'])
        ql.add_row([np.sqrt((query['idf'].loc[preprocessing(q)] ** 2).sum()).round(4)])
        print(ql)

        create_table(summary_table, 'Cosine Similarity', '')

        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)

        result_dict = {}
        rd = pt(['Returned Docs'])
        for doc_id, score in sorted_scores:
            rd.add_row([doc_id])
            result_dict[doc_id] = score
        print(rd)

        return result_dict
    else:
        print("You entered words that's not in the files")
        query = input('Enter Your Query: ')
        insert_query(query)



def split_query(q):

    parts = re.split(f"({'|'.join(operators)})", q)
    # Remove empty strings from the list
    parts = [part for part in parts if part]
    return parts


def anding(phrases):
    try:
        and_index = phrases.index('AND')
    except ValueError:
        and_index = None

    if and_index is not None:
        common_keys = set(phrases[and_index - 1].keys()).intersection(phrases[and_index + 1].keys())

        # Create a new dictionary with common keys and values
        common_elements = {}
        for key in common_keys:
            common_elements[key] = phrases[and_index - 1][key]

        phrases[and_index - 1: and_index + 2] = [common_elements]
    return phrases

def oring(phrases):
    try:
        or_index = phrases.index('OR')
    except ValueError:
        or_index = None

    if or_index is not None:
        combined_keys = set(phrases[or_index - 1].keys()).union(phrases[or_index + 1].keys())

        # Create a new dictionary with combined keys and values
        combined_elements = {}
        for key in combined_keys:
            combined_elements[key] = phrases[or_index - 1].get(key, None) or phrases[or_index + 1].get(key, None)

        phrases[or_index - 1: or_index + 2] = [combined_elements]

    return phrases



def noting(phrases):
    try:
        not_index = phrases.index('NOT')
    except ValueError:
        not_index = None

    if not_index is not None:
        # Create a new set with the keys from the previous element excluding keys in the current element
        not_elements = set(phrases[not_index - 1].keys()) - set(phrases[not_index + 1].keys())

        if not not_elements:  # If the set is empty
            # Remove the 'NOT' index and the index after it
            del phrases[not_index : not_index + 2]
        else:
            # Replace the elements with the new set
            phrases[not_index - 1 : not_index + 2] = [not_elements]

    return phrases



def boolean_query(q):
    phrases = split_query(q)
    for i in range(len(phrases)):
        phrase = phrases[i]
        if phrase.upper() not in operators:
            print(phrase)
            result = insert_query(phrase)
            phrases[i] = result


    anding(phrases)
    oring(phrases)
    noting(phrases)

    # Order the dictionary by values
    sorted_phrases = dict(sorted(phrases[0].items(), key=lambda item: item[1], reverse=True))

    table = pt(['Final Returned Docs'])
    for key in sorted_phrases.keys():
        table.add_row([key])
#
    return table

