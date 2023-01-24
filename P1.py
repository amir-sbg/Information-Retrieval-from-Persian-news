from hazm import *
import json

f = open('documents.json')
data = json.load(f)

normalizer = Normalizer()
normal_content_list = []

for i in data:
    normal_content = normalizer.normalize(data[i]['content'])
    normal_content_list.append(normal_content)
    # print(normal_content)

word_tokenize_list = []
for normal_content in normal_content_list:
    word_tokenize_list.append(word_tokenize(normal_content))

# print(len(word_tokenize_list))
# for i in range(10):
#     print(word_tokenize_list[i])


lemmatizer = Lemmatizer()
word_lem_list = []

for word_list in word_tokenize_list:
    temp_list = []
    for word in word_list:
        word = lemmatizer.lemmatize(word)

        temp_list.append(word)

    word_lem_list.append(temp_list)



word_stem_list = []
stemmer = Stemmer()
for word_list in word_tokenize_list:
    temp_list = []
    for word in word_list:
        word = stemmer.stem(word)

        temp_list.append(word)

    word_stem_list.append(temp_list)


repeate_words = ['و',')','(','به']
word_final_list = word_stem_list
index_dict = {}  # {word(1):{all_reapeat:number,doc_id(n):[location1,...,loacation(n)]}}
for doc_id in range(len(word_final_list)):
    doc_word_list = word_final_list[doc_id]
    counter = 0
    for word in doc_word_list:

        try:
            index_dict[word]['all_repeate'] += 1
        except:
            index_dict[word] = {'all_repeate': 1, 'doc_id_list': [doc_id]}

        if doc_id not in index_dict[word]['doc_id_list']:
            index_dict[word]['doc_id_list'].append(doc_id)

        try:
            index_dict[word][doc_id].append(counter)
        except:
            index_dict[word][doc_id] = [counter]

        counter += 1



print(index_dict['فوتسال'])
print(index_dict['AFC'])
print(index_dict['فوتبال'])
#all_repeate
#doc_id_list

query  = "فوتسال AFC ! فوتبال"
tokenized_query = word_tokenize(query)

print(tokenized_query)



documents_scores = {}
not_list=[]
being_in_document_score, repeating_in_document_score = 20, 1
for idx,word_item in enumerate(tokenized_query):
    if '!' in word_item and idx != len(tokenized_query)-1:
        print("Not:",tokenized_query[idx+1])
        not_list=not_list+index_dict[tokenized_query[idx+1]]['doc_id_list']
    else:
        for posting in index_dict[word_item]['doc_id_list']:
            try:
                documents_scores[posting]
                # Scoring base on existing in the document
                documents_scores[posting] = documents_scores[posting] + being_in_document_score
                # Scoring base on number of repeated times in the document
                documents_scores[posting] = documents_scores[posting] + (
                            (len(index_dict[word_item][posting]) - 1) * repeating_in_document_score)

            except:
                documents_scores[posting] = being_in_document_score
                documents_scores[posting] = documents_scores[posting] + (
                            (len(index_dict[word_item][posting]) - 1) * repeating_in_document_score)
for id in not_list:
    try:
        documents_scores[id]
        documents_scores.pop(id)
    except:
        pass



sort_orders = sorted(documents_scores.items(), key=lambda x: x[1], reverse=True)

for idx, i in enumerate(sort_orders):
	print(f'{idx+1:>6}',"nd      DocID:",f'{i[0]:<10}',"Score: ",f'{i[1]:<10}')
