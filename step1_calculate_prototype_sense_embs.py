import xlrd
import numpy as np
import pickle
import torch
from transformers import BertModel, BertTokenizer, AdamW
import os
import glob
'''
该文件旨在计算每个词义的“原型向量”
首先需要解析 .xlsx 标注语料库，并对每个意义的所有相关 BERT embedding 进行平均

This file aims to calculate all the "prototype embedding" of each sense
We need to parse the annotated .xlsx corpus and do the averaging of each sense's all concerned BERT embedding
'''

def convert_corpus_to_sense_dicts(filename):
    '''
    从标注语料库xlsx文件中提取出每个字的每个义项的语料
    并写成字典的形式，字典的key是字，value是一个字典B，字典B的key是义项，value是一个列表，列表中是解释为该义项的所有包含目标词word的语料
    
    Extract the corpus of each sense of each word from the annotation corpus xlsx file
    And write in the format of a dictionary, the key of the dictionary is the word, the value is a dictionary B, the key of the dictionary B is the sense, the value is a list, and the list is the sentences containing the word in this sense
    '''

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
    for row in corpus_row_list:
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


def get_lastlayer_emb_from_model(text, target, model, tokenizer, device):
    
    '''
    从BERT模型的输出层中获取目标词的embedding
    Obtain the embedding of the target word from the output layer of the BERT model
    '''
    tokenized_text = tokenizer.tokenize(text)  #token初始化
    tokenized_text = ["[CLS]"] + tokenized_text + ["[SEP]"]
    #print(tokenized_text)
    indexed_tokens = tokenizer.convert_tokens_to_ids(tokenized_text)  #获取词汇表索引
    #print(text,tokenized_text,indexed_tokens)

    tokens_tensor = torch.tensor([indexed_tokens])  #将输入转化为torch的tensor
    tokens_tensor = tokens_tensor.to(device)
    target_positions = [tokenized_text.index(char) for char in tokenized_text if char == target]
    if not target_positions and target in ['曷','泅']: # [UNK] in BERT vocabulary
        target_positions = [tokenized_text.index(char) for char in tokenized_text if char == '[UNK]']
    tokenized_size = len(tokens_tensor[0])

    outputs = model(tokens_tensor, output_hidden_states=True)
    #outputs.to_tuple() #transformers 4.0以上需要
    #print("len_outputs:",len(outputs),outputs)#outputs[0]是为跳阶段的分类概率，outputs[1]是每一层向量
    all_emb = outputs[-1][-1].to(device)  #如果有分类层，[-1]其实为[1]，否则为唯一的维度[0]
    
    avg_target_emb = torch.zeros([768]).to(device)
    for po in target_positions:
        avg_target_emb += all_emb[0][po].to(device)

    avg_target_emb = avg_target_emb / len(target_positions)
    avg_target_emb_np = np.array(avg_target_emb.detach().cpu())
    return avg_target_emb_np


def get_prototypes(dic: dict, wd: str, out_dir: str, full_mode: bool):  #dic：{word:{sense1:[sent1,sent2]}}
    '''
    full_mode: 对语料库中所有词义都计算原型向量
    cut_mode: 对语料库中词义例句数大于5的才计算原型向量

    full_mode: Compute prototype vectors for all word senses in the corpus
    cut_mode: The prototype vector is calculated only when the number of word sense examples in the corpus is greater than 5
    '''
    if full_mode:
        threshold = 0
    else:
        threshold = 5
    all_sent_dic = dic
    sense_emb_dic = {}  #{word{sense1:emb,sense2:emb},word2}
    if wd in all_sent_dic:
        sensesents = all_sent_dic[wd]  #sensesents: {sense1:[sent1,sent2], sense2:[sent1,sent2]}
        sense_emb_dic[wd] = {}
        for sense, sents in sensesents.items():
            if len(sents) >= threshold:
                added_emb = np.zeros(768)
                cnt = 0
                for sent in sents:
                    if sent:
                        avg_target_emb_np = get_lastlayer_emb_from_model(
                            sent, wd, model, tokenizer, device)
                        
                        added_emb += avg_target_emb_np
                        cnt += 1
                if cnt > 0:
                    avg_emb = added_emb / cnt
                    sense_emb_dic[wd][sense] = avg_emb
                
            else:
                print(f"{wd}," + sense + "例句数量不足 not enough examples")
        with open(f"{out_dir}/{wd}_prototypes.dic", "wb") as wt:
            pickle.dump(sense_emb_dic, wt)
            print("已处理：processed word: ", wd)
    else:
        print(f"错误：目标词不在已标注语料中。error: word is not in the annotated corpus: {wd}")




if __name__ == "__main__":

    # use GPU
    os.environ["CUDA_VISIBLE_DEVICES"] = "0"
    if torch.cuda.is_available():
        device = torch.device("cuda")
        print('There are %d GPU(s) available.' % torch.cuda.device_count())
    else:
        print('No GPU available, using the CPU instead.')
        device = torch.device("cpu")
    tokenizer = BertTokenizer(
        vocab_file='/siku-simp-bert/vocab.txt')
    
    # load BERT
    PRE_TRAINED_MODEL_NAME = "/siku-simp-bert"
    model = BertModel.from_pretrained(PRE_TRAINED_MODEL_NAME)
    model = model.to(device)
    model.eval()


    filename = 'data/20230508_icip_ancient_chinese_annotation_corpus.xlsx' #语料库excel文件位置 The place of the .xlsx annotated corpus
    out_dir = "output_data/sense_prototypes_fullmode" #原型向量输出位置 output direction of prototype vectors
    if not os.path.exists(out_dir):
        os.mkdir(out_dir)
    already_done = glob.glob(out_dir + "/*")
    already_done_words = []
    for f in already_done:
        already_done_words.append(os.path.split(f)[-1][0])

    dic = convert_corpus_to_sense_dicts(filename)

    target_chars = ['亡', '氏', '报', '心', '济', '令', '奔', '道', '素', '备', '宗', '文', '私', '勒', '适', '长', '许', '忠', '卒', '责', '要', '即', '生', '虚', '达', '视', '迁', '归', '尽', '诚', '史', '诵', '加', '赤', '求', '佛', '比', '逾', '致', '去', '进', '明', '通', '劝', '仁', '穿', '从', '次', '尚', '解', '下', '病', '微', '兵', '若', '怠', '汉', '征', '谒', '举', '相', '遇', '问', '谦', '末', '短', '完', '委', '时', '工', '修', '凶', '智', '闻', '城', '宾', '立', '坐', '属', '情', '公', '论', '直', '后', '负', '死', '族', '胜', '故', '和', '说', '引', '将', '睡', '鲜', '钱', '徐', '务', '宜', '规', '借', '曾', '多', '恨', '华', '忘', '间', '拔', '患', '熙', '汤', '类', '幼', '仙', '君', '前', '释', '孝', '白', '戚', '欲', '具', '池', '悟', '左', '义', '克', '却', '少', '幸', '日', '固', '讽', '暴', '黑', '内', '怨', '旁', '灵', '喻', '敝', '图', '退', '率', '朴', '畜', '化', '育', '遂', '假', '休', '走', '卧', '玉', '老', '为', '笃', '见', '乃', '知', '发', '临', '得', '寐', '冲', '姓', '师', '太', '谢', '博', '大', '王', '乘', '本', '读', '潜', '殆', '奇', '礼', '德', '今', '国', '期', '偃', '涕', '倍', '阴', '会', '或', '念', '中', '何', '璞', '制', '事', '朝', '莫', '夺', '至', '善', '夏', '能', '眠', '出', '稍', '绝', '看', '当', '意', '里', '慕', '寝', '竟', '存', '如', '按', '上', '复', '敌', '既', '识', '处', '陵', '质', '币', '请', '胡', '数', '除', '鄙', '望', '诣', '作', '爱', '就', '诸', '造', '过', '使', '趋', '饯', '非', '籍', '未', '判', '秀', '自', '居', '性', '及', '行', '堪', '贻', '省', '弛', '孰', '教', '紫', '青', '恶', '任', '传', '著', '门', '弥', '名', '山', '清', '神', '书', '安', '贼', '黄', '易', '穷', '兴', '度', '涉', '言', '静', '阳', '信', '振', '辞', '遗', '伪', '方', '疾', '察', '俾', '虞', '延', '红', '家', '被', '泪', '怜', '益', '治', '是', '第', '来', '正', '儒', '置', '理', '与', '而', '让', '便', '徒', '顺', '元', '右', '悉', '顾', '节', '徙', '泅', '肪', '嘴', '肚', '皆', '疼', '亮', '男', '夫', '彼', '女', '妇', '毛', '牙', '齿', '种', '子', '杀', '弑', '戮', '游', '泳', '众', '我', '吾', '余', '予', '尔', '汝', '谁', '不', '弗', '肤', '皮', '肉', '肌', '鸟', '禽', '狗', '犬', '羽', '路', '夜', '夕', '晓', '燃', '焚', '燔', '烧', '寡', '绿', '干', '燥', '膏', '脂', '首', '头', '目', '眼', '口', '足', '趾', '脚', '领', '颈', '项', '腹', '根', '啮', '噬', '咬', '步', '执', '持', '秉', '握', '把', '捉', '语', '云', '曰', '谓', '话', '朱', '盈', '满', '良', '吉', '佳', '此', '斯', '兹', '奚', '曷', '咸', '佥', '胥', '俱', '均', '总', '川', '水', '江', '河', '巨', '硕', '树', '木', '止', '停', '息', '住', '忧', '愁', '虑', '昭', '显', '彰', '久', '极', '最', '逸', '入', '始', '初', '肇', '快', '悦', '乐', '喜', '确', '痛', '思', '想', '恭', '敬', '好', '美', '倾', '覆']
    
    for char in target_chars:
        get_prototypes(dic, char, out_dir, True)
