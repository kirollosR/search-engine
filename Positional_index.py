def create_positional_index(document_of_terms):
    document_number = 0
    positional_index = {}

    for document in document_of_terms:

        # For position and term in the tokens.
        for positional, term in enumerate(document):
            # print(pos, '-->' ,term)

            # If term already exists in the positional index dictionary.
            if term in positional_index:

                # Increment total freq by 1.
                positional_index[term][0] = positional_index[term][0] + 1

                # Check if the term has existed in that DocID before.
                if document_number in positional_index[term][1]:
                    positional_index[term][1][document_number].append(positional)

                else:
                    positional_index[term][1][document_number] = [positional]

            # If term does not exist in the positional index dictionary
            # (first encounter).
            else:

                # Initialize the list.
                positional_index[term] = []
                # The total frequency is 1.
                positional_index[term].append(1)
                # The postings list is initially empty.
                positional_index[term].append({})
                # Add doc ID to postings list.
                positional_index[term][1][document_number] = [positional]

        # Increment the file no. counter for document ID mapping
        document_number += 1
    return positional_index

def print_positional_index(positional_index):
    print('Positional index')

    for key, value in positional_index.items():
        # Check if the value is a list with at least two elements and the second element is a dictionary
        if isinstance(value, list) and len(value) >= 2 and isinstance(value[1], dict):
            # Print the key and the key-value pairs of the inner dictionary on a single line
            print(f"{key}: \"{value[0]}\" {' '.join(f'{k}: {v}' for k, v in value[1].items())}")
    print('-' * 80 + '\n')