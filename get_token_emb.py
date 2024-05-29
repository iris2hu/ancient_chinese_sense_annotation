import xlrd
import re
from bert_serving.client import BertClient
import numpy as np
import pickle as p

bc = BertClient()

def prep_text(word, sent, sid):
    '''
    data preprocessing: filter out the inadequate sentences
    '''
    if word not in sent:
        print(word, 'not in sent', sent)
        return None
    elif 's' not in sid:
        # /, 待定, 语料不宜等
        # print(word, sid, 'not qualified')
        return None

    sent = sent.replace(' ', '')
    sent = sent.replace('[' + word + ']', word)
    if word[0] not in sent[:126]:
        print('sentence length exceeds the limit:', len(sent), sent)
        return None

    return sent

# load data

data = xlrd.open_workbook('data/20230508_icip_ancient_chinese_annotation_corpus.xlsx')
sheet = data.sheets()[2]
rownum = sheet.nrows

word_dict = {}

for i in range(1,rownum):

    row = sheet.row_values(i)
    word, sense, sent, sid = row[2], row[3], row[4], row[5]
    word = word[0]  # 去除数字标记，如复1/复2/复3
    sent = prep_text(word, sent, sid)
    if not sent:
        continue
    if word not in word_dict:
        word_dict[word] = [(sid, sense, sent)]
    else:
        word_dict[word].append((sid, sense, sent))

print('loaded data of {} words'.format(len(word_dict)))

for k,v in word_dict.items():
    print('word: {}, has {} sentences to be processed'.format(k, len(v)))

    # get token embeddings

    input_sents = [x[-1] for x in v]
    vec = bc.encode(input_sents, show_tokens=True)
    all_arrays, all_tokens = vec

    data = []
    
    for tid in range(len(all_tokens)):
        # load sentence information
        sid, sense, sent = v[tid]
        tokens = all_tokens[tid]
        arrays = all_arrays[tid]
        target_embs = []

        # get the target word embeddings
        for i in range(len(tokens)):
            token = tokens[i]
            if token == k:
                # print(i, token, k, sense, sent, 'True')
                emb = arrays[i]
                target_embs.append(emb)

        if target_embs:
            data.append([k, sid, sense, sent, target_embs])

    # export to npz file
    
    with open('./data/pickle_files/' + k + '.pickle', 'wb') as f:
        p.dump(data, f)

    print('sucessfully processed {} sentences...'.format(len(data)))






