import xlrd
import re
import numpy as np
import pickle as p
import torch
import transformers
import pandas as pd
import glob
from transformers import BertModel, BertTokenizer
import os

os.environ["CUDA_VISIBLE_DEVICES"] = "0"
if torch.cuda.is_available():      
    device = torch.device("cuda")
    print('There are %d GPU(s) available.' % torch.cuda.device_count())
else:
    print('No GPU available, using the CPU instead.')
    device = torch.device("cpu")
    
    
PRE_TRAINED_MODEL_NAME = "siku_simp_bert"
p_model = BertModel.from_pretrained(PRE_TRAINED_MODEL_NAME)
tokenizer = BertTokenizer(vocab_file='siku_simp_bert/vocab.txt')

def get_lastlayer_emb_from_model(text,target,input_model):
    model = input_model
    model = model.to(device)
    model.eval()
    '''
    evaluation mode
    '''
    tokenized_text = tokenizer.tokenize(text) #token初始化
    #print(tokenized_text)
    tokenized_text = ["[CLS]"] + tokenized_text + ["[SEP]"]
    indexed_tokens = tokenizer.convert_tokens_to_ids(tokenized_text) #获取词汇表索引
    tokens_tensor = torch.tensor([indexed_tokens]) #将输入转化为torch的tensor
    tokens_tensor = tokens_tensor.to(device)
    target_positions = []
    for idx, char in enumerate(tokenized_text):
        if char == target:
            target_positions.append(idx)
    tokenized_size = len(tokens_tensor[0])

    outputs = model(tokens_tensor,output_hidden_states=True)
    #outputs.to_tuple() #transformers 4.0以上需要
    # print(text)
    # print(len(outputs))
    # print(len(outputs[-1]))
    # print(len(outputs[-1][-1][0]))
    
    all_emb = outputs[-1][-1][0].to(device)
    avg_target_emb = torch.zeros([1,768]).to(device)
    for po in target_positions:
        avg_target_emb += all_emb[po].to(device)
    avg_target_emb = avg_target_emb/len(target_positions)
    avg_target_emb_np = np.array(avg_target_emb.detach().cpu())
    return avg_target_emb_np

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
    word = word[0]  # 去除同形词的数字标记，如复1/复2/复3
    sent = prep_text(word, sent, sid)
    if not sent:
        continue
    if word not in word_dict:
        word_dict[word] = [(sid, sense, sent)]
    else:
        word_dict[word].append((sid, sense, sent))

print('loaded data of {} words'.format(len(word_dict)))

if os.path.exists("data/pickle_files") == False:
    os.mkdir("data/pickle_files")
processed = glob.glob("data/pickle_files/*")
processed_word = [i[-8] for i in processed]

for k,v in word_dict.items():
    if k not in processed_word:
        #picklefile的形式：word写在文件名里。存的是list，每一个item也是List,[target, sid, sense, sent, tar_vec]
        print('word: {}, has {} sentences to be processed'.format(k, len(v)))
        target = k
        # get token embeddings
        data = []
        for tp in v:#each tuple is (sid, sense, sent)
            sent = tp[-1]
            sense = tp[1]
            sid = tp[0]
            tar_vec = get_lastlayer_emb_from_model(sent,target,p_model)

            #if tar_vec:
            data.append([target, sid, sense, sent, tar_vec])

    # export to npz file
    
        with open('data/pickle_files/' + k + '.pickle', 'wb') as f:
            p.dump(data, f)

        print('sucessfully processed {} sentences...'.format(len(data)))

