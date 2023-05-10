import xlrd 
'''
这个文件展示了解析语料库xlsx文件的方式
随意更改该函数，可以提取您想要的任何字段

This file shows the way to parse the corpus xlsx file
Feel free to alter the function to get whatever feature you want
'''

filename = '20230508_icip_ancient_chinese_annotation_corpus.xlsx'
def convert_corpus_to_sense_dicts(filename):
    data = xlrd.open_workbook(filename)
    sense_list = data.sheets()[1]
    corpus = data.sheets()[2]

    nrows_corpus = corpus.nrows  #获取sheet2中的有效行数
    corpus_row_list = []
    for i in range(nrows_corpus):
        line = corpus.row_values(i, start_colx=0, end_colx=None)
        if line[0]:
            corpus_row_list.append(line)
    ret = {}
    for row in corpus_row_list[1:]:
        word = row[2][0]
        sense_discrip = row[3]
        sent = row[4]
        sent = sent.replace("[", "")
        sent = sent.replace(" ", "")
        sent = sent.replace("]", "")
        sense_id = row[5]
        sense_id_and_discrip = sense_id + "-" + sense_discrip
        
        if word not in ret:
            ret[word] = {}
        if sense_id_and_discrip not in ret[word]:
            ret[word][sense_id_and_discrip] = [sent]
        if sense_id_and_discrip in ret[word]:
            ret[word][sense_id_and_discrip].append(sent)
    return ret

sense_dict = convert_corpus_to_sense_dicts(filename)
single_sense_words = {}
for k,v in sense_dict.items():
    if len(v) == 1:
        single_sense_words[k] = v

print("知识库总收词数：concerned words:", len(sense_dict))

print("单义词：single-sense words:",len(single_sense_words), single_sense_words.keys())