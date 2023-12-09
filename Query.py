from Preprocessing import preprocessing

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