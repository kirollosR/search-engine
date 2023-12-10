from Preprocessing import preprocessing
from Vector_space import normalized_term_freq_idf, idf, create_table
import math
import numpy as np
import pandas as pd


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
    product_result = product2[list(scores.keys())].loc[preprocessing(q)]
    return product_result, scores


def check_words_in_index(dataframe, word_list):
    # Get the index of the DataFrame
    index_words = dataframe.index.tolist()

    # Check if all words in the list are present in the index
    return all(word in index_words for word in word_list)


def insert_query(q):
    query = pd.DataFrame(index=normalized_term_freq_idf.index)
    query['tf'] = [1 if x in preprocessing(q) else 0 for x in list(normalized_term_freq_idf.index)]
    query['w_tf'] = query['tf'].apply(lambda x: get_w_tf(x))

    # Use loc to set values in the original DataFrame
    query.loc[:, 'idf'] = idf['idf'] * query['w_tf']
    query.loc[:, 'tf_idf'] = query['w_tf'] * query['idf']

    # Use loc to set values in the original DataFrame
    query['normalized'] = (query['idf'] / np.sqrt((query['idf'] ** 2).sum())).astype(float).round(3)

    found_in_index = check_words_in_index(query, preprocessing(q))

    if found_in_index:
        create_table(query, 'Query Details')

        product_result, scores = product_query(q, query)

        create_table(product_result, 'Product (query*matched doc)')
        print()
        print('product sum')
        print(product_result.sum())
        print()
        print('Query Length')
        q_len = np.sqrt((query['idf'].loc[preprocessing(q)] ** 2).sum())
        print(q_len)
        print()
        print('Cosine Similarity')
        print(product_result.sum())
        print()

        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)

        print('Returned docs')
        for doc_id, score in sorted_scores:
            print(doc_id)
