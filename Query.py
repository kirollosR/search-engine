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
    found_in_index = check_words_in_index(query, preprocessing(q))

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


def boolean_query(q):
    phrases = split_query(q)
    for i in range(len(phrases)):
        phrase = phrases[i]
        if phrase.upper() not in operators:
            print(phrase)
            result = insert_query(phrase)
            phrases[i] = result

    return phrases


def process_boolean_operations(query_result):
    operators = ["AND", "OR", "NOT"]

    while any(op in operators for op in query_result):
        for i in range(len(query_result)):
            if query_result[i] in operators:
                operator = query_result[i]
                if operator == "NOT":
                    operand = query_result[i + 1]
                    # Check if the next operator is AND, indicating "AND NOT"
                    next_operator = query_result[i + 2] if i + 2 < len(query_result) else None
                    if next_operator == "AND":
                        and_not_result = perform_and_not_operation(query_result[i - 1], operand)
                        query_result.pop(i - 1)  # Remove the left operand
                        query_result.pop(i - 1)  # Remove the "AND"
                        query_result.pop(i - 1)  # Remove the "NOT"
                        query_result.pop(i - 1)  # Remove the right operand
                        query_result.insert(i - 1, and_not_result)
                    else:
                        query_result.pop(i)  # Remove NOT operator
                        query_result.pop(i)  # Remove the operand
                        result = perform_not_operation(operand)
                        query_result.insert(i - 1, result)
                else:
                    left_operand = query_result[i - 1]
                    right_operand = query_result[i + 1]
                    query_result.pop(i - 1)  # Remove the left operand
                    query_result.pop(i - 1)  # Remove the operator
                    query_result.pop(i - 1)  # Remove the right operand
                    if operator == "AND":
                        result = perform_and_operation(left_operand, right_operand)
                    elif operator == "OR":
                        result = perform_or_operation(left_operand, right_operand)
                    query_result.insert(i - 1, result)
                break

    return query_result[0]


def perform_and_operation(left_operand, right_operand):
    common_docs = set(left_operand.keys()) & set(right_operand.keys())
    return list(common_docs)

def perform_or_operation(left_operand, right_operand):
    # Combine documents from both operands
    combined_docs = set(left_operand.keys()) | set(right_operand.keys())
    return list(combined_docs)


def perform_not_operation(operand, all_documents=None):
    # Invert the set of documents from the operand
    if all_documents is None:
        all_documents = ["doc1", "doc2", "doc3", "doc4", "doc5", "doc6", "doc7", "doc8", "doc9", "doc10"]
    not_docs = set(all_documents) - set(operand.keys())
    return list(not_docs)

def perform_and_not_operation(left_operand, not_operand):
    # Find common documents with left_operand and remove those from not_operand
    common_docs = set(left_operand.keys()) & set(not_operand.keys())
    result = {doc: left_operand[doc] for doc in common_docs}
    return result
