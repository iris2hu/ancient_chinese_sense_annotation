from __future__ import division
import pandas as pd
import numpy as np
import decimal,glob,re
import pickle as p
import os
import matplotlib.pyplot as plt
import matplotlib as mpl
import sys
from matplotlib.font_manager import fontManager

'''
根据大规模标注结果，画出每个词多个义项的历史趋势图
According to the results of large-scale annotation, the historical trend chart of multiple meanings of each word is drawn
'''

def multinomial_fitting(x,y,k=4):
    # to make the curves smmooth
    z = np.polyfit(x, y, k)
    poly = np.poly1d(z)
    y_fitting = [poly(xx) for xx in x]
    return y_fitting

def get_distribution_matrix(each_word_dic):
    diac = ["先秦","汉","魏晋六朝","隋唐五代","宋","元明","清至民初"]
    sense_counts={}
    different_senses = set()

    for dynasty,sent_with_tag in each_word_dic.items():
        if dynasty not in sense_counts:
            sense_counts[dynasty] = {}
            for tp in sent_with_tag:
                text, predict = tp
                if predict:
                    predict = predict.replace(" ","")
                    if predict not in different_senses:
                        different_senses.add(predict)
                    if predict not in sense_counts[dynasty]:
                        sense_counts[dynasty][predict] = 1
                    else:
                        sense_counts[dynasty][predict] += 1
                
    # print("different_senses:",different_senses)
    try:
        l_senses = sorted(list(different_senses),key = lambda x:("".join(re.findall("^\d+",x)), int(re.findall("s\d+",x)[0][1:]), x))
    except:
        l_senses = sorted(list(different_senses),key = lambda x:x)
    sense_count = len(different_senses)
    distribution = pd.DataFrame(columns=l_senses)
    
    distribution["朝代/义项"] = diac
    distribution.set_index(["朝代/义项"],inplace=True)
    distribution = distribution.fillna(0.000001)

    for dyna,sense_count in sense_counts.items():
        for sense,count in sense_count.items():
            distribution.at[dyna,sense] = count
    # print("distribution")
    # print(distribution)
    matrix = distribution.astype('float')
    for d in diac:
        sums = sum(list(distribution.loc[d,:]))
        # print("朝代",d,"总句子数",sums)
        for sense in l_senses:
            matrix.at[d,sense] = distribution.at[d,sense]/sums
    # for dyna in diac:
        # print("时代：",dyna,"概率总和",sum(matrix.loc[dyna].to_list()))
    return matrix


if __name__ == "__main__":
    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_rows',None)
    diac = ["先秦","汉","魏晋六朝","隋唐五代","宋","元明","清至民初"]

    song_path = 'utils/simsun.ttf'
    fontManager.addfont(song_path)
    prop = mpl.font_manager.FontProperties(fname=song_path)
    mpl.rcParams['font.family'] = prop.get_name()
    ALL_Color = ['red','green','black','deepskyblue','gold','darkviolet','k',"c","magenta"] 
    ALL_Point = ['^','+','o','D','.','*',"s","h"]

    tagged_sents_dir = "data/tagged_sents_fullmode"
    all_tagged_sents_file = glob.glob(tagged_sents_dir + "/*.dic")
    save_path = "output_data/历时分布图/"
    if not os.path.exists(save_path):
        os.mkdir(save_path)
    
    for f in all_tagged_sents_file:
        # parse the labeled sentences, write into txt files
        with open(f,"rb")as rf:
            each_word_dic = p.load(rf)
        word = os.path.split(f)[-1][-5]
        
        write_lines = []
        output_raw_dir = save_path + word+"自动标注源文件（准确率约80%）.txt"
        if not os.path.exists(output_raw_dir):
            output_lines = []
            for dynasty,sent_with_tag in each_word_dic.items():
                for tp in sent_with_tag:
                    text, predict = tp
                    write_lines.append(f"{dynasty}\t{text}\t{predict}\n")
            with open(output_raw_dir, "w")as wf:
                for l in write_lines:
                    wf.write(l)

    
    plotted = []
    already_exists = glob.glob(save_path + "*.png")
    for f in already_exists:
        w = f.split("/")[-1][0]
        plotted.append(w)
    not_plotted = []

    for f in all_tagged_sents_file:
        with open(f,"rb")as rf:
            each_word_dic = p.load(rf)
        word = os.path.split(f)[-1][-5]
        
        print(word)
      
        sense_counts = {}
        for dynasty,sent_with_tag in each_word_dic.items():
            if dynasty not in sense_counts:
                sense_counts[dynasty] = {}
                for tp in sent_with_tag:
                    text, predict = tp
                    if predict:
                        predict = predict.replace(" ","")
                        if predict not in sense_counts[dynasty]:
                            sense_counts[dynasty][predict] = 1
                        else:
                            sense_counts[dynasty][predict] += 1

        matrix = get_distribution_matrix(each_word_dic)
        fitted_data = pd.DataFrame()
        sense_count = matrix.shape[1]
        senses = list(matrix.columns)[:]
        # print("senses in matrix:",senses)
        
        
        plt.rc('legend', fontsize = 15) 
        plt.rcParams['axes.unicode_minus'] = False
        plt.tick_params(labelsize=13)
        plt.figure(figsize=(10,8))
        for i in range(sense_count):
            y = list(matrix.iloc[:,i])
            sense = senses[i]
            dynas = [0,1,2,3,4,5,6]
            fitted_y = multinomial_fitting(dynas,y,k=4)
            for j in range(len(fitted_y)):
                if fitted_y[j] < 0:
                    fitted_y[j] = 0

            x = diac
            fitted_data[sense] = fitted_y
            fitted_data.rename(index={0: "先秦", 1: "汉", 2: "魏晋六朝",3:"隋唐五代",4:"宋",5:"元明",6:"清至民初"})
            plt.scatter(x, y, marker = ALL_Point[(i-1)%(len(ALL_Point))], color = ALL_Color[(i-1)%len(ALL_Color)], label=senses[i])
            plt.plot(x, fitted_y, linestyle='--',color = ALL_Color[(i-1)%len(ALL_Color)])
            #plt.title('polyfitting')
        
            legend = plt.legend(loc=2, bbox_to_anchor=(1.05,1.0))
            legend.get_frame()
        plt.xlabel('朝代',size = 22)
        plt.ylabel('义项频次占比',size = 22)
        plt.savefig(save_path+"%s历时分布.png"%word, bbox_inches='tight')
                

        
        