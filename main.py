from Preprocessing import load_data, print_data
from Positional_index import create_positional_index, print_positional_index
from Vector_space import tf_table, weighted_tf_table, idf_table, tf_idf_table, document_length_table, normalized_tf_idf_table
from Query import positional_index_query

document_of_terms = load_data()
print_data(document_of_terms)

positional_index = create_positional_index(document_of_terms)
print_positional_index(positional_index)

tf_table()
weighted_tf_table()
idf_table()
tf_idf_table()
document_length_table()
normalized_tf_idf_table()

query = input('Enter Your Query: ')
print("Matched docs using positional index: ")
print(positional_index_query(query, positional_index))