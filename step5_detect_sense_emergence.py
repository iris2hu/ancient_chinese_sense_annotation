from __future__ import division
import os
import re
import pickle as p

def get_distribution_list(each_word_dic):

    '''
    根据学位论文，确定词义产生时代需要满足的条件：
    ① 目标义项在当前时代所有义项频次总和中，占比大于等于λ1
    ② 目标义项在这个义项的历史频次总和中占比大于等于λ2
    ③ 目标义项在当前时代的出现频次≥χ

    因此需要获得目标义项在当前时代所有义项频次总和中的占比 和 目标义项在这个义项的历史频次总和中的占比

    '''
    diac_map = ["先秦", "汉", "魏晋六朝", "隋唐五代", "宋", "元明", "清至民初"]

    sense_counts = {}
    # {dynasty1:{sense1:count1, sense2:count2, sense3:count3}, dynasty2:{}}
    different_senses = set()

    for dynasty, sent_with_tag in each_word_dic.items():
        if dynasty not in sense_counts:
            sense_counts[dynasty] = {}
            for tp in sent_with_tag:
                text, predict = tp
                if predict:
                    predict = predict.replace(" ", "")
                    if predict not in different_senses:
                        different_senses.add(predict)
                    if predict not in sense_counts[dynasty]:
                        sense_counts[dynasty][predict] = 1
                    else:
                        sense_counts[dynasty][predict] += 1
                else:
                    print(text, predict)
    try:
        l_senses = sorted(list(different_senses),
                        key=lambda x: int(re.findall("\d+", x)[0]))
    except:
        l_senses = sorted(list(different_senses))
    sense_num = len(different_senses)

    freq_lst = [[0 for _ in range(7)] for _ in range(len(l_senses))]

    for dyna, sense_count in sense_counts.items():
        for sense, count in sense_count.items():
            freq_lst[l_senses.index(sense)][diac_map.index(dyna)] = count

    era_slice_ratio_lst = [[0 for _ in range(7)] for _ in range(len(l_senses))]
    for era in range(7):
        cur_era_sum = sum(list(zip(*freq_lst))[era]) if sum(
            list(zip(*freq_lst))[era]) != 0 else 0.00001
        for sense_idx in range(len(l_senses)):
            era_slice_ratio_lst[sense_idx][
                era] = freq_lst[sense_idx][era] / cur_era_sum  # type: ignore
    #print("era_slice_ratio_lst", era_slice_ratio_lst)

    sense_slice_ratio_lst = [[0 for _ in range(7)]
                             for _ in range(len(l_senses))]
    for sense_idx in range(sense_num):
        cur_sense_sum = sum(freq_lst[sense_idx])
        for era in range(7):
            sense_slice_ratio_lst[sense_idx][
                era] = freq_lst[sense_idx][era] / cur_sense_sum  # type: ignore
    #print("sense_slice_ratio_lst", sense_slice_ratio_lst)
    return l_senses, freq_lst, era_slice_ratio_lst, sense_slice_ratio_lst


def detect_novel_sense(l_senses, era_slice_ratio_lst, sense_slice_ratio_lst,
                       freq_lst, lambda1, lambda2, threshold):
    diac_map = ["先秦", "汉", "魏晋六朝", "隋唐五代", "宋", "元明", "清至民初"]

    sense_emerge_time = [0] * len(l_senses)  #返回的列表，长度为义项数量，lst[i] 为义项i产生的时代  The returned list is the length of the number of senses and lst[i] is the era in which the sense i was produced
    for sense_idx in range(len(l_senses)):
        if "s1-" in l_senses[sense_idx]: #s1是默认的本义，在先秦产生 S1 is the default original meaning, which was produced in the pre-Qin dynasty
            sense_emerge_time[sense_idx] = 0
            continue
        for t in range(7):
            if era_slice_ratio_lst[sense_idx][t] >= lambda1 \
                or sense_slice_ratio_lst[sense_idx][t] >= lambda2 \
                and freq_lst[sense_idx][t] >= threshold:
                sense_emerge_time[sense_idx] = t
                break
                
    sense_appear_dic = {}
    for sense_idx, emerge_t in enumerate(sense_emerge_time):
        #print(l_senses[sense_idx], diac_map[emerge_t])
        sense_appear_dic[l_senses[sense_idx]] = diac_map[emerge_t]

    sense_fade_dic = {}
    # #义项消失的判断：同时满足在当前时代所有义项频率中小于20%、当前义项所有时代中小于20%、频次总量<5，且每个时代都如此，持续到结束
    # for sense_idx in range(len(l_senses)):
    #     at_low = []
    #     for timestep in range(7):
    #         if timestep > sense_emerge_time[sense_idx]:  #must have emerged
    #             if era_slice_ratio_lst[sense_idx][timestep] < 0.2 \
    #             and sense_slice_ratio_lst[sense_idx][timestep] < 0.2 \
    #             and freq_lst[sense_idx][timestep] < 10:
    #                 at_low.append(timestep)
        

    #     popped_diac = []
    #     #只有当at_low连续增加直到6的，才算消失的义项
    #     if at_low and at_low[-1] == 6:
    #         while len(at_low) >= 2 and at_low[-1] - at_low[-2] == 1:
    #             p = at_low.pop()
    #             popped_diac.append(p)
    #     if popped_diac: #存在义项消失的情况
    #         start_disappear_time = popped_diac[-1] - 1
    #         sense_fade_dic[l_senses[sense_idx]] = diac_map[start_disappear_time]
    return sense_appear_dic, sense_fade_dic


if __name__ == "__main__":
    target_words = ['亡', '氏', '报', '心', '济', '令', '奔', '道', '素', '备', '宗', '文', '私', '勒', '适', '长', '许', '忠', '卒', '责', '要', '即', '生', '虚', '达', '视', '迁', '归', '尽', '诚', '史', '诵', '加', '赤', '求', '佛', '比', '逾', '致', '去', '进', '明', '通', '劝', '仁', '穿', '从', '次', '尚', '解', '下', '病', '微', '兵', '若', '怠', '汉', '征', '谒', '举', '相', '遇', '问', '谦', '末', '短', '完', '委', '时', '工', '修', '凶', '智', '闻', '城', '宾', '立', '坐', '属', '情', '公', '论', '直', '后', '负', '死', '族', '胜', '故', '和', '说', '引', '将', '睡', '鲜', '钱', '徐', '务', '宜', '规', '借', '曾', '多', '恨', '华', '忘', '间', '拔', '患', '熙', '汤', '类', '幼', '仙', '君', '前', '释', '孝', '白', '戚', '欲', '具', '池', '悟', '左', '义', '克', '却', '少', '幸', '日', '固', '讽', '暴', '黑', '内', '怨', '旁', '灵', '喻', '敝', '图', '退', '率', '朴', '畜', '化', '育', '遂', '假', '休', '走', '卧', '玉', '老', '为', '笃', '见', '乃', '知', '发', '临', '得', '寐', '冲', '姓', '师', '太', '谢', '博', '大', '王', '乘', '本', '读', '潜', '殆', '奇', '礼', '德', '今', '国', '期', '偃', '涕', '倍', '阴', '会', '或', '念', '中', '何', '璞', '制', '事', '朝', '莫', '夺', '至', '善', '夏', '能', '眠', '出', '稍', '绝', '看', '当', '意', '里', '慕', '寝', '竟', '存', '如', '按', '上', '复', '敌', '既', '识', '处', '陵', '质', '币', '请', '胡', '数', '除', '鄙', '望', '诣', '作', '爱', '就', '诸', '造', '过', '使', '趋', '饯', '非', '籍', '未', '判', '秀', '自', '居', '性', '及', '行', '堪', '贻', '省', '弛', '孰', '教', '紫', '青', '恶', '任', '传', '著', '门', '弥', '名', '山', '清', '神', '书', '安', '贼', '黄', '易', '穷', '兴', '度', '涉', '言', '静', '阳', '信', '振', '辞', '遗', '伪', '方', '疾', '察', '俾', '虞', '延', '红', '家', '被', '泪', '怜', '益', '治', '是', '第', '来', '正', '儒', '置', '理', '与', '而', '让', '便', '徒', '顺', '元', '右', '悉', '顾', '节', '徙', '泅', '肪', '嘴', '肚', '皆', '疼', '亮', '男', '夫', '彼', '女', '妇', '毛', '牙', '齿', '种', '子', '杀', '弑', '戮', '游', '泳', '众', '我', '吾', '余', '予', '尔', '汝', '谁', '不', '弗', '肤', '皮', '肉', '肌', '鸟', '禽', '狗', '犬', '羽', '路', '夜', '夕', '晓', '燃', '焚', '燔', '烧', '寡', '绿', '干', '燥', '膏', '脂', '首', '头', '目', '眼', '口', '足', '趾', '脚', '领', '颈', '项', '腹', '根', '啮', '噬', '咬', '步', '执', '持', '秉', '握', '把', '捉', '语', '云', '曰', '谓', '话', '朱', '盈', '满', '良', '吉', '佳', '此', '斯', '兹', '奚', '曷', '咸', '佥', '胥', '俱', '均', '总', '川', '水', '江', '河', '巨', '硕', '树', '木', '止', '停', '息', '住', '忧', '愁', '虑', '昭', '显', '彰', '久', '极', '最', '逸', '入', '始', '初', '肇', '快', '悦', '乐', '喜', '确', '痛', '思', '想', '恭', '敬', '好', '美', '倾', '覆']

    for word in target_words:
        print(word)
        try:
            with open(f"output_data/tagged_sents_fullmode/tagged_sents_{word}.dic", "rb") as rdf:
                each_word_dic = p.load(rdf)
                l_senses, freq_lst, era_slice_ratio_lst, sense_slice_ratio_lst = get_distribution_list(
                    each_word_dic)
                sense_appear_dic, sense_fade_dic = detect_novel_sense(
                    l_senses, era_slice_ratio_lst, sense_slice_ratio_lst, freq_lst,
                    0.32, 0.04, 2) # 0.32, 0.04, 2来源于参数网格搜索的实验结果  0.32, 0.04, 2 are decided by the experimental results of the parametric grid search
                if not os.path.exists("output_data/sense_emergence_time"):
                    os.mkdir("output_data/sense_emergence_time")
                with open(f"output_data/sense_emergence_time/{word}_emerge.dic", "wb")as dp1:
                    p.dump(sense_appear_dic, dp1)

        except:
            pass
        