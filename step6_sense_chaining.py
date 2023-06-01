import numpy as np
from numpy.linalg import norm
import pickle as p
from collections import defaultdict
import re
import os

'''
根据step5_detect_sense_emergence.py获得的词义产生时代推断（存储在“sense_emergence_time_fullmode”）
进一步计算词义的引申关系，得到词义引申树的字典形式，存在chained_results_fullmode文件夹中
'''

def cos_simi(A, B):
    A = np.asarray(A, dtype='float64')
    B = np.asarray(B, dtype='float64')
    return np.dot(A, B)/(norm(A)*norm(B))

           
def one_nn_chaining(vec, sense_to_select: dict):
    biggest_similarty = 0
    most_similar_ancestor = ""
    for sense, vec2 in sense_to_select.items():
        
        if cos_simi(vec, vec2) > biggest_similarty:
            biggest_similarty = cos_simi(vec, vec2)
            most_similar_ancestor = sense
    return most_similar_ancestor


def chaining_each_word(prototype_dir, emerge_time_dir, word):
    with open("data/pinyin_mapping.dic","rb")as pinyin_map:
        pinyin_mapping = p.load(pinyin_map)
    try:
        with open(f'{prototype_dir}/{word}_prototypes.dic', "rb") as ptt:
            cur_word_prototypes = p.load(ptt)
            sense_vector_dic = cur_word_prototypes[word]
            sense_vector_dic_new = {k: v for k, v in sense_vector_dic.items() if not re.findall("通“.”|s0", k)}
            sense_vector_dic = sense_vector_dic_new
        with open(f"{emerge_time_dir}/{word}_emerge.dic", "rb") as emg:
            sense_emerge_dic = p.load(emg)  # {sense_idx: emerge_epoch}
        # 规则：去除通假义项
        sense_emerge_dic = {k: v for k, v in sense_emerge_dic.items() if not re.findall("通“.”|s0", k)}
        t0_senses = [k for k, v in sense_emerge_dic.items() if v == '先秦']  # original senses
        # print("初始义项：", t0_senses)
        # 先秦就有的义项
        existing_senses = {k: v for k, v in sense_vector_dic.items() if k in t0_senses}  # key:sense_id, val:vector

        diac_map = ["先秦", "汉", "魏晋六朝", "隋唐五代", "宋", "元明", "清至民初"]
        chain_graph = defaultdict(dict)
        for s in t0_senses:
            chain_graph[s]['from'] = None

        for i in range(0, 7):
            cur_dynasty = diac_map[i]
            new_emerge_senses = [k for k, v in sense_emerge_dic.items() if v == cur_dynasty]  # senses appear at this timestep
            # to chain the new sense to old senses
            for each_sense in new_emerge_senses:
                #加同音规则
                cur_pinyin = pinyin_mapping[word].get(each_sense)
                vec = sense_vector_dic.get(each_sense)
                #only select same sound senses in ancestors
                sense_to_select = {k: v for k, v in existing_senses.items() if not cur_pinyin or pinyin_mapping[word].get(k) == cur_pinyin}
                if sense_to_select and vec is not None:
                    most_similar_ancestor = one_nn_chaining(vec, sense_to_select)
                    #print(cur_dynasty, each_sense, "从", most_similar_ancestor, "引申而来")
                    chain_graph[each_sense]['from'] = most_similar_ancestor
                    chain_graph[each_sense]['emerge_time'] = cur_dynasty
                    if not chain_graph[most_similar_ancestor].get('to'):
                        chain_graph[most_similar_ancestor]['to'] = [each_sense]
                    else:
                        chain_graph[most_similar_ancestor]['to'].append(each_sense)
                else:
                    #print(cur_dynasty, each_sense,"从",list(existing_senses.keys()),"找不到引申来源")
                    pass
            for new_s in new_emerge_senses:
                existing_senses[new_s] = sense_vector_dic.get(new_s)

        return chain_graph
    except:
        return {}

def parsing_chain_graph_to_pairs(chain_graph):
    anticident_pairs = {}
    for sense, dic in chain_graph.items():
        for k,sense2 in dic:
            if sense2 == "from": #it has anticident
                anticident_pairs[sense] = sense2
    return anticident_pairs

if __name__ == "__main__":
    target_words = ['亡', '氏', '报', '心', '济', '令', '奔', '道', '素', '备', '宗', '文', '私', '勒', '适', '长', '许', '忠', '卒', '责', '要', '即', '生', '虚', '达', '视', '迁', '归', '尽', '诚', '史', '诵', '加', '赤', '求', '佛', '比', '逾', '致', '去', '进', '明', '通', '劝', '仁', '穿', '从', '次', '尚', '解', '下', '病', '微', '兵', '若', '怠', '汉', '征', '谒', '举', '相', '遇', '问', '谦', '末', '短', '完', '委', '时', '工', '修', '凶', '智', '闻', '城', '宾', '立', '坐', '属', '情', '公', '论', '直', '后', '负', '死', '族', '胜', '故', '和', '说', '引', '将', '睡', '鲜', '钱', '徐', '务', '宜', '规', '借', '曾', '多', '恨', '华', '忘', '间', '拔', '患', '熙', '汤', '类', '幼', '仙', '君', '前', '释', '孝', '白', '戚', '欲', '具', '池', '悟', '左', '义', '克', '却', '少', '幸', '日', '固', '讽', '暴', '黑', '内', '怨', '旁', '灵', '喻', '敝', '图', '退', '率', '朴', '畜', '化', '育', '遂', '假', '休', '走', '卧', '玉', '老', '为', '笃', '见', '乃', '知', '发', '临', '得', '寐', '冲', '姓', '师', '太', '谢', '博', '大', '王', '乘', '本', '读', '潜', '殆', '奇', '礼', '德', '今', '国', '期', '偃', '涕', '倍', '阴', '会', '或', '念', '中', '何', '璞', '制', '事', '朝', '莫', '夺', '至', '善', '夏', '能', '眠', '出', '稍', '绝', '看', '当', '意', '里', '慕', '寝', '竟', '存', '如', '按', '上', '复', '敌', '既', '识', '处', '陵', '质', '币', '请', '胡', '数', '除', '鄙', '望', '诣', '作', '爱', '就', '诸', '造', '过', '使', '趋', '饯', '非', '籍', '未', '判', '秀', '自', '居', '性', '及', '行', '堪', '贻', '省', '弛', '孰', '教', '紫', '青', '恶', '任', '传', '著', '门', '弥', '名', '山', '清', '神', '书', '安', '贼', '黄', '易', '穷', '兴', '度', '涉', '言', '静', '阳', '信', '振', '辞', '遗', '伪', '方', '疾', '察', '俾', '虞', '延', '红', '家', '被', '泪', '怜', '益', '治', '是', '第', '来', '正', '儒', '置', '理', '与', '而', '让', '便', '徒', '顺', '元', '右', '悉', '顾', '节', '徙', '泅', '肪', '嘴', '肚', '皆', '疼', '亮', '男', '夫', '彼', '女', '妇', '毛', '牙', '齿', '种', '子', '杀', '弑', '戮', '游', '泳', '众', '我', '吾', '余', '予', '尔', '汝', '谁', '不', '弗', '肤', '皮', '肉', '肌', '鸟', '禽', '狗', '犬', '羽', '路', '夜', '夕', '晓', '燃', '焚', '燔', '烧', '寡', '绿', '干', '燥', '膏', '脂', '首', '头', '目', '眼', '口', '足', '趾', '脚', '领', '颈', '项', '腹', '根', '啮', '噬', '咬', '步', '执', '持', '秉', '握', '把', '捉', '语', '云', '曰', '谓', '话', '朱', '盈', '满', '良', '吉', '佳', '此', '斯', '兹', '奚', '曷', '咸', '佥', '胥', '俱', '均', '总', '川', '水', '江', '河', '巨', '硕', '树', '木', '止', '停', '息', '住', '忧', '愁', '虑', '昭', '显', '彰', '久', '极', '最', '逸', '入', '始', '初', '肇', '快', '悦', '乐', '喜', '确', '痛', '思', '想', '恭', '敬', '好', '美', '倾', '覆']
    prototype_dir = "output_data/sense_prototypes_fullmode"
    emerge_time_dir = "output_data/sense_emergence_time_fullmode"
    
    for word in target_words:
        print('=====================')
        print(word)
        chain_graph = chaining_each_word(prototype_dir, emerge_time_dir, word)
        if not os.path.exists("output_data/chained_results_fullmode"):
            os.mkdir("output_data/chained_results_fullmode")
        with open(f"output_data/chained_results_fullmode/{word}chained_senses.dic", "wb")as pkf:
            p.dump(chain_graph, pkf)
