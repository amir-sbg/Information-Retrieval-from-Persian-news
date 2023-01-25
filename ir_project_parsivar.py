#!/usr/bin/env python
# coding: utf-8

# In[ ]:


get_ipython().system('pip install parsivar')


# In[ ]:


import parsivar


# In[ ]:


import json


# # reading file

# In[ ]:


f = open('IR_data_news_12k.json')
data = json.load(f)


# # preprocessing : normalizing

# In[ ]:


from parsivar import Normalizer
normalizer = Normalizer()
normal_content_list = []


# In[ ]:


for i in data:
    normal_content = normalizer.normalize(data[i]['content'])
    normal_content_list.append(normal_content)
    print(normal_content)


# # preprocessing : tokenizing

# In[ ]:


from parsivar import Tokenizer
word_tokenizer = Tokenizer()
word_tokenize_list = []
for normal_content in normal_content_list:
    word_tokenize_list.append(word_tokenize(normal_content))


# In[ ]:


print(len(word_tokenize_list))
for i in range(10):
    print(word_tokenize_list[i])


# # preprocessing : Stemming 

# In[ ]:


from parsivar import FindStems
stemmer = FindStems()


# In[ ]:


word_stem_list = []

for word_list in word_tokenize_list:
    temp_list = []
    for word in word_list:
        
        word = stemmer.convert_to_stem(word)        
        
        temp_list.append(word)
        
    word_stem_list.append(temp_list)


# In[ ]:


print(word_stem_list[0])


# # preprocessing : removing very Repeated words

# In[ ]:


blacklist = {'؟', 'است', '}', '{', ')', '(', 'شد', '@', ':', '*', '.', '،', '\\', '/', '<', '>', '?', '!', '@', ':',
             ':', '.', 'از', 'به', 'در', 'این', 'آن', 'ها', 'با',
             'کرد', 'را', 'کرد', 'شود', 'این', 'آن', 'تا', '1',
             'است', 'بود', 'داد', 'برای', '-', '=', '_', 'ها', 'که',
             'اش', '...', ',', 'ما', 'اما', 'من', 'هم',
             'او', 'کند', 'بر', 'نیز', 'هر', 'اگر', 'پس',
             'خود', 'کند', 'کرد&کن', 'داشت&دار', 'خواست&خواه', 'گرفت&گیر', 'توانست&توان',
             'که', 'و'}


# # indexing 

# In[ ]:


word_final_list = word_stem_list


# In[ ]:


index_dict = {} # {word(1):{all_reapeat:number,doc_id(n):[location1,...,loacation(n)]}}
for doc_id in range(len(word_final_list)):
    doc_word_list = word_final_list[doc_id]
    counter = 0
    for word in doc_word_list:
        try:
            index_dict[word]['all_repeate'] += 1
        except:
            index_dict[word] = {'all_repeate': 1,'doc_id_list':[doc_id]}
            
        
        if doc_id not in index_dict[word]['doc_id_list']:
            index_dict[word]['doc_id_list'].append(doc_id)
        
        try:
            index_dict[word][doc_id].append(counter)
        except:
            index_dict[word][doc_id] = [counter]


        counter += 1


# In[ ]:


len(index_dict)


# In[ ]:


index_withot_black_list ={}
for word in index_dict:
    if word not in blacklist:
        index_withot_black_list[word] = index_dict[word]


# In[ ]:


len(index_withot_black_list)


# In[ ]:


print(index_dict['فوتسال'])
print(index_dict['AFC'])
#all_repeate
#doc_id_list


# # preprocessing query

# In[ ]:


def standarding_query(query):
    normal_query = normalizer.normalize(query)
    word_tokenize_list = word_tokenize(normal_query)
    
    lem_list =[]
    for word in word_tokenize_list:
        
        word = lemmatizer.lemmatize(word)
        
        lem_list.append(word)
    
    stem_list = []
    for word in lem_list:
        
        word = stemmer.stem(word)        
        
        stem_list.append(word)
    return stem_list


# # user query 
# 

# In[ ]:


query  = " تحریم های آمریکا علیه ایران"
tokenized_query = standarding_query(query)
# tokenized_query = word_tokenize(query)
# print(tokenized_query)


# In[ ]:


query  = "تحریم های آمریکا ! ایران"
tokenized_query = standarding_query(query)
print(tokenized_query)


# In[ ]:


query  = "کنگره ضدتروریست"
tokenized_query = standarding_query(query)
print(tokenized_query)


# In[ ]:


query  = " تحریم هسته ای آمریکا ! ایران"
tokenized_query = standarding_query(query)
print(tokenized_query)


# In[ ]:


query  = " اورشلیم ! صهیونیست"
tokenized_query = standarding_query(query)
print(tokenized_query)


# ## scoring documents in order to respond to user's queries 
# 

# In[ ]:


documents_scores = {}
not_list = []
being_in_document_score, repeating_in_document_score = 20, 1
being_next_to_each_other=1000
for idx, word_item in enumerate(tokenized_query):
    if '!' in word_item and idx != len(tokenized_query) - 1:
        print("Not:", tokenized_query[idx + 1])
        not_list = not_list + index_dict[tokenized_query[idx + 1]]['doc_id_list']
    else:
        for posting in index_dict[word_item]['doc_id_list']:
            try:
                documents_scores[posting]
                # Scoring base on existing in the document
                documents_scores[posting] = documents_scores[posting] + being_in_document_score
                # Scoring base on number of repeated times in the document
                documents_scores[posting] = documents_scores[posting] + (
                        (len(index_dict[word_item][posting]) - 1) * repeating_in_document_score)
                if idx != 0:
                    if not '!' in tokenized_query[idx - 1]:
                        for sec in index_dict[word_item][posting]:
                            try:
                                for fir in index_dict[tokenized_query[idx - 1]][posting]:
                                    if sec == fir + 1:
                                        documents_scores[posting] = documents_scores[posting] + being_next_to_each_other
                            except:
                                pass


            except:
                documents_scores[posting] = being_in_document_score
                documents_scores[posting] = documents_scores[posting] + (
                        (len(index_dict[word_item][posting]) - 1) * repeating_in_document_score)
                if idx != 0:
                    if not '!' in tokenized_query[idx - 1]:
                        for sec in index_dict[word_item][posting]:
                            try:
                                for fir in index_dict[tokenized_query[idx - 1]][posting]:
                                    if sec == fir + 1:
                                        documents_scores[posting] = documents_scores[posting] + being_next_to_each_other
                            except:
                                pass
                            
for id in not_list:
    try:
        documents_scores[id]
        documents_scores.pop(id)
    except:
        pass

sort_orders = sorted(documents_scores.items(), key=lambda x: x[1], reverse=True)

for idx, i in enumerate(sort_orders):
    print(f'{idx + 1:>6}', "nd      DocID:", f'{i[0]:<10}', "Score: ", f'{i[1]:<10}')


# In[ ]:


def five_best_score(sort_orders):
    counter = 0
    for item in sort_orders:
        doc_id = item[0]
        if counter == 5:
            break
        counter += 1
        print(data[str(doc_id)]['url'])
        print(data[str(doc_id)]['title'])
        print('**************************')


# In[ ]:


# query 1 : تحریم های آمریکا علیه ایران
five_best_score(sort_orders)


# In[ ]:


# query 2 :  تحریمهای آمریکا ! ایران
five_best_score(sort_orders)


# In[ ]:


# query 3 : کنگره ضدتروریست
five_best_score(sort_orders)


# In[ ]:


# query 4 : " تحریم هستهای" آمریکا ! ایران
five_best_score(sort_orders)


# In[ ]:


# query 5 : اورشلیم ! صهیونیست
five_best_score(sort_orders)

