import xlrd
import re
import pickle as p

data = xlrd.open_workbook("四库总集古文提取示例_已标点.xlsx")
song_data = data.sheets()[0]
yuan_data = data.sheets()[1]
min_data = data.sheets()[2]
qing_data = data.sheets()[3]

  #获取sheet2中的有效行数
def cut_sentences(article, spliters):
    sents_from_article = []
    cur_sent = ''
    for char in article:
        cur_sent += char
        if char in spliters:
            sents_from_article.append(cur_sent)
            cur_sent = ''
    return sents_from_article

def create_each_dynasty_sents(dynasty_data):
    nrows_corpus = dynasty_data.nrows
    corpus_row_list = []
    for i in range(nrows_corpus):
        line = dynasty_data.row_values(i, start_colx=0, end_colx=None)
        corpus_row_list.append(line)
    
    dynasty_sents = []
    for row in corpus_row_list:
        book = row[2]
        genre = row[3]
        article = row[6]
        article = re.sub("<span class=.*?</span>","", article)
        article = article.replace("<p>", "")
        spliters = ["。","？","！"]
        sents_from_article = cut_sentences(article, spliters)
        dynasty_sents.extend([book, genre, s] for s in sents_from_article if 7 < len(s) < 500)
    return dynasty_sents

yuan_sents = create_each_dynasty_sents(yuan_data)
min_sents = create_each_dynasty_sents(min_data)
qing_sents = create_each_dynasty_sents(qing_data)

yuanmin_sents = yuan_sents + min_sents


all_sents = {}
all_sents["元明"] = yuanmin_sents
all_sents["清至民初"] = qing_sents
print(len(all_sents["元明"]))
print(len(all_sents["清至民初"]))

with open("augment.dic", "wb")as wf:
    p.dump(all_sents, wf)



