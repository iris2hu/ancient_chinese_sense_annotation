import pickle as p
import glob, os
from random import shuffle
import numpy as np
from numpy import linalg as la
import pandas as pd
import sys

def cosSimilarity(A,B):
    vector1 = np.mat(A)
    vector2 = np.mat(B)
    cosV12 = float(vector1*vector2.T)/(la.norm(vector1)*la.norm(vector2))
    return cosV12

def tag_sense(emb, sense_d):
    result, max_simi = None, 0
    for sk, se in sense_d.items():
        simi = cosSimilarity(emb, se)
        if simi > max_simi:
            result, max_simi = sk, simi
    return result, max_simi


def sense_training_testing(pickle_file, threshold=2):
    '''
    pickle_file: word.pickle
    '''

    with open(pickle_file, 'rb') as f:
        d = p.load(f)

    # get sense info
    sense_dict = {}

    for info in d:
        word, sid, sense, sent, sense_embs = info
        sk = sid.strip() + '-' + sense.strip()
        if sk not in sense_dict:
            sense_dict[sk] = [[sk, sent, sense_embs]]
        else:
            sense_dict[sk].append([sk, sent, sense_embs])

    origin_sent_num = len(d)
    origin_sense_num = len(sense_dict)

    # select the training and testing senses based on threshold
    sense_dict = {k:v for k,v in sense_dict.items() if len(v) >= threshold}
    select_sense_num = len(sense_dict)
    train_num, test_num = 0, 0
    sense_embeddings = {} #to store the sense vector calculated by train data
    test_data_all = []

    for sk, info in sense_dict.items():
        
        # train_test split

        shuffle(info)
        if len(info) < 5:
            # 1 sentence for test when there are 2-4 example sentences
            cutoff_num = len(info) - 1
        else:
            # 20% of sentences for test when there are >= 5 sentences
            cutoff_num = round(len(info) * 0.8)

        train_data, test_data = info[:cutoff_num], info[cutoff_num:]
        train_num += len(train_data)
        test_num += len(test_data)
        test_data_all.extend(test_data)

        # build sense embeddings with train data

        tmp_embs = []
        for t in train_data:
            tmp_embs.extend(t[-1])

        sense_embeddings[sk] = sum(tmp_embs) / len(tmp_embs)

    # for test
    test_results = []
    for answer, sent, sense_embs in test_data_all:
        for emb in sense_embs:
            predict, similarity = tag_sense(emb, sense_embeddings)
            test_results.append([word, sent, answer, predict, str(similarity)])

    return origin_sent_num, origin_sense_num, select_sense_num, train_num, test_num, test_results


if __name__ == '__main__':

    freq_threshold = sys.argv[1]
    tag_file = './data/tag_result_threshold.txt'
    stats_file = './data/statistics_threshold.csv'
    tag_file = tag_file.replace('threshold', 'threshold_' + freq_threshold)
    stats_file = stats_file.replace('threshold', 'threshold_' + freq_threshold)

    files = glob.glob('data/pickle_files/*.pickle')

    
    statistics = [['origin_sent_num', 'origin_sense_num', 'select_sense_num', 'train_num', 'test_num']]

    with open(tag_file, 'w', encoding="utf-8") as f:

        all_test_num, correct_num, wrong_num,correct_prob,wrong_prob = 0, 0, 0, 0, 0
        #all_test_num, correct_num = 0, 0
        for i, file in enumerate(files):
            word = file[-8]
            origin_sent_num, origin_sense_num, select_sense_num, train_num, test_num, test_results = sense_training_testing(file, threshold=int(freq_threshold))
            statistics.append([origin_sent_num, origin_sense_num, select_sense_num, train_num, test_num])

            all_test_num += test_num
            
            for tag_info in test_results:
                if tag_info[-2] == tag_info[-3]:
                    correct_num += 1
                    correct_prob += float(tag_info[-1]) #============new added
                else:
                    wrong_num += 1
                    wrong_prob += float(tag_info[-1]) 
                tag_info = [str(i) for i in tag_info] 
                newline = '\t'.join(tag_info) + '\n'
                f.write(newline)

        df = pd.DataFrame(statistics)
        df.to_csv(stats_file, index=False)
        print("all_test_num",all_test_num)
        print("correct_num",correct_num)
        print(freq_threshold, 'top-1 accuracy:', correct_num/all_test_num, "true_avg_prob:", correct_prob/correct_num, "false_avg_prob:", wrong_prob/wrong_num)
