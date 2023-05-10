import glob, os
import re
from collections import defaultdict
import pickle as p

'''
本文件的功能是预处理从从“语料库在线”中下载的对应每个字的语料并去重。并从《四库总集》中补充元明清的语料。

corpus_file_dir 装的是从“语料库在线”中下载的txt文件，有些是分时代下载的。无论是分时代下载还是整体下载，都需要涵盖这个词的所有语料
函数compile_each_word_corpus 的作用是，把一个词的所有语料合并在一起，然后按照时代划分，
“语料库在线”中收录的《兵法》，内容来自于不同时代，而“语料库在线”将它分配在先秦，不符合事实，因此直接删除
函数re_assign_timespan 的作用是：
因为《全唐文》和《醒世姻缘》在语料库在线中没有分对时代，需要重新分配到对应的时代
函数 augment_corpus_with_target_words 的作用是：由于“语料库在线”收录的语料明清较少，需要另外从四库全书中补充语料
最后，将每个字的所有历史语料打包好，放在compiled_dic_output_dir 中

The use of this file is to preprocess the corpus corresponding to each word downloaded from "corpus online" and delete all duplicated lines. And supplement the corpus of Yuan, Ming and Qing Dynasties from "Siku Zongji".

corpus_file_dir contains txt files downloaded from Corpus Online, some downloaded by each era, some by all eras. In any case, they are all meant to collect all the corpus of the word
The function compile_each_word_corpus is to combine all the corpus of a word and divide it according to era.
The content of the "Art of War" included in "Corpus Online" comes from different eras, and "Corpus Online" assigns it to the pre-Qin dynasty, which is not in line with the facts, so it is directly deleted
The function re_assign_timespan does:
Because "Quan Tang Wen" and "Awakening Marriage" are not divided into pairs of eras in the corpus online, they need to be reassigned to the corresponding eras
The function augment_corpus_with_target_words is that because there are fewer corpus included in "Corpus Online", it is necessary to supplement the corpus from the four libraries
Finally, pack up all the historical corpus for each word and put it in compiled_dic_output_dir
'''

def compile_each_word_corpus(word, corpus_file_dir):
    '''
    从“语料库在线(http://corpus.zhonghuayuwen.org/)”上按时代下载的语料，一个字有多个文件，放在raw_corpus中。
    按照字，把同一个字的多个文件合并

    The corpus downloaded from "Corpus Online(http://corpus.zhonghuayuwen.org/)" by era, one word has multiple files, and placed in raw_corpus.
    Merge multiple files of the same word according to the word
    '''
    raw_corpus_dir = f"{corpus_file_dir}/*.txt"
    raw_files = glob.glob(raw_corpus_dir) #all files containing this word

    duplicated = 0
    compiled_dic = {}
    compiled_dic[word] = {}
    for f in raw_files: 
        last_file_name = os.path.split(f)[-1]
        cur_wd = last_file_name[0]

        if cur_wd == word:
            with open(f, "r") as rdf:
                for line in rdf:
                    if "__" in line:
                        line = re.sub("[\]\[]", "", line)
                        line = line.replace(" ", "")
                        num, sent, _, book = line.split("\t")
                        dynasty = book.split("_")[-1].replace("\n", "")
                        book_name = book.split("_")[0]
                        if book_name != "《兵法》":
                            # to join dynasties
                            if dynasty in ["周", "春秋战国"]:
                                dynasty = "先秦"
                            if dynasty in ["清", "民初"]:
                                dynasty = "清至民初"
                            if dynasty not in compiled_dic[word]:
                                compiled_dic[word][dynasty] = [(sent, book_name)]
                            elif (sent, book_name) in compiled_dic[word][
                                dynasty
                            ]:
                                duplicated += 1
                            else:  # delete replication
                                compiled_dic[word][dynasty].append((sent, book_name))
    return compiled_dic
    

def re_assign_timespan(compiled_dic):
    #rule1: 《全唐文》is assigned in Qing Dynasty in http://corpus.zhonghuayuwen.org/, put it in Suitangwudai Dynasty
    for wd, dynasty_dic in compiled_dic.items():
        #print("add qtw before:", len(compiled_dic[wd]["隋唐五代"]), len(compiled_dic[wd]["清至民初"]))
        all_quantangwen = []
        for dynasty, sent_list in dynasty_dic.items():
            new_sent_list = []
            for tp in sent_list:
                sent, book_name = tp
                if book_name == "《全唐文》" and dynasty != "隋唐五代":
                    all_quantangwen.append(sent)
                else:
                    new_sent_list.append(tp) # all sentences apart from 《全唐文》
            compiled_dic[wd][dynasty] = new_sent_list
        for s in all_quantangwen:
            if (s, "《全唐文》") not in compiled_dic[wd]["隋唐五代"]:
                compiled_dic[wd]["隋唐五代"].append((s, "《全唐文》"))
        #print("add qtw after:", len(compiled_dic[wd]["隋唐五代"]), len(compiled_dic[wd]["清至民初"]))
    
    #rule2:《醒世姻缘》put into Yuanming Dynasty
    for wd, dynasty_dic in compiled_dic.items():
        #print("add xsyy before:", len(compiled_dic[wd]["元明"]), len(compiled_dic[wd]["清至民初"]))
        all_xsyy = []
        for dynasty, sent_list in dynasty_dic.items():
            new_sent_list = []
            for tp in sent_list:
                sent, book_name = tp
                if book_name == "《醒世姻缘》" and dynasty != "元明":
                    all_xsyy.append(sent)
                else:
                    new_sent_list.append(tp) # all sentences apart from 《醒世姻缘》
            compiled_dic[wd][dynasty] = new_sent_list
        for s in all_xsyy:
            if (s, "《醒世姻缘》") not in compiled_dic[wd]["元明"]:
                compiled_dic[wd]["元明"].append((s, "《醒世姻缘》"))
        #print("add xsyy after:", len(compiled_dic[wd]["元明"]), len(compiled_dic[wd]["清至民初"]))

    return compiled_dic

def augment_corpus_with_target_words(compiled_dic, augmented_sents):
    '''
    compiled_dic : {word1:{dynasty1:[s1,s2,s3]}}
    Since the corpus amount is insufficient in Yuan, Ming, Qing dynasties,
    we add more corpus from《四库总集》
    
    '''
    augment_ratio_dic = defaultdict(dict)
    aug_count = 0
    target_words = list(compiled_dic.keys())
    for w in target_words:
        for dynasty in augmented_sents.keys():
            cur_word_dynasty_augment = 0
            dynasty_lst = augmented_sents[dynasty]
            for book, genre, s in dynasty_lst:
                if w in s:
                    if compiled_dic[w].get(dynasty) and s not in compiled_dic[w][dynasty]:
                        book_simple = re.sub("卷.*?$","",book) #增量语料里面，书名还带卷数
                        compiled_dic[w][dynasty].append((s, "《" + book_simple + "》"))
                        #print("增加了:", s, "目标词语：", w)
                        sents_count_in_cur_dynasty = len(compiled_dic[w][dynasty])
                        cur_word_dynasty_augment += 1
                        aug_count += 1
                    if not compiled_dic[w].get(dynasty): #语料库在线中的语料太少，不包含这个朝代
                        book_simple = re.sub("卷.*?$","",book) #增量语料里面，书名还带卷数
                        compiled_dic[w][dynasty] = []
                        compiled_dic[w][dynasty].append((s, "《" + book_simple + "》"))
                        #print("增加了:", s, "目标词语：", w)
                        sents_count_in_cur_dynasty = len(compiled_dic[w][dynasty])
                        cur_word_dynasty_augment += 1
                        aug_count += 1
            aug_ratio = round(cur_word_dynasty_augment / sents_count_in_cur_dynasty, 4)
            augment_ratio_dic[w][dynasty] = aug_ratio
    print("总共增加：added: ", aug_count)

    return compiled_dic, augment_ratio_dic
    
if __name__ == "__main__":

    compiled_dic_output_dir = "data/compiled_corpus" #元明清数据增量后的
    corpus_file_dir = "data/raw_corpus"
    augmet_sents_dir = "data/data_augment/augment.dic"

    already_done = glob.glob(compiled_dic_output_dir + "/*")
    already_done_words = []
    for f in already_done:
        already_done_words.append(os.path.split(f)[-1][0])
    print("already_done_words", already_done_words)
    #read augment sents
    with open(augmet_sents_dir,"rb") as augm:
        augmented_sents = p.load(augm)

    target_chars = ['亡', '氏', '报', '心', '济', '令', '奔', '道', '素', '备', '宗', '文', '私', '勒', '适', '长', '许', '忠', '卒', '责', '要', '即', '生', '虚', '达', '视', '迁', '归', '尽', '诚', '史', '诵', '加', '赤', '求', '佛', '比', '逾', '致', '去', '进', '明', '通', '劝', '仁', '穿', '从', '次', '尚', '解', '下', '病', '微', '兵', '若', '怠', '汉', '征', '谒', '举', '相', '遇', '问', '谦', '末', '短', '完', '委', '时', '工', '修', '凶', '智', '闻', '城', '宾', '立', '坐', '属', '情', '公', '论', '直', '后', '负', '死', '族', '胜', '故', '和', '说', '引', '将', '睡', '鲜', '钱', '徐', '务', '宜', '规', '借', '曾', '多', '恨', '华', '忘', '间', '拔', '患', '熙', '汤', '类', '幼', '仙', '君', '前', '释', '孝', '白', '戚', '欲', '具', '池', '悟', '左', '义', '克', '却', '少', '幸', '日', '固', '讽', '暴', '黑', '内', '怨', '旁', '灵', '喻', '敝', '图', '退', '率', '朴', '畜', '化', '育', '遂', '假', '休', '走', '卧', '玉', '老', '为', '笃', '见', '乃', '知', '发', '临', '得', '寐', '冲', '姓', '师', '太', '谢', '博', '大', '王', '乘', '本', '读', '潜', '殆', '奇', '礼', '德', '今', '国', '期', '偃', '涕', '倍', '阴', '会', '或', '念', '中', '何', '璞', '制', '事', '朝', '莫', '夺', '至', '善', '夏', '能', '眠', '出', '稍', '绝', '看', '当', '意', '里', '慕', '寝', '竟', '存', '如', '按', '上', '复', '敌', '既', '识', '处', '陵', '质', '币', '请', '胡', '数', '除', '鄙', '望', '诣', '作', '爱', '就', '诸', '造', '过', '使', '趋', '饯', '非', '籍', '未', '判', '秀', '自', '居', '性', '及', '行', '堪', '贻', '省', '弛', '孰', '教', '紫', '青', '恶', '任', '传', '著', '门', '弥', '名', '山', '清', '神', '书', '安', '贼', '黄', '易', '穷', '兴', '度', '涉', '言', '静', '阳', '信', '振', '辞', '遗', '伪', '方', '疾', '察', '俾', '虞', '延', '红', '家', '被', '泪', '怜', '益', '治', '是', '第', '来', '正', '儒', '置', '理', '与', '而', '让', '便', '徒', '顺', '元', '右', '悉', '顾', '节', '徙', '泅', '肪', '嘴', '肚', '皆', '疼', '亮', '男', '夫', '彼', '女', '妇', '毛', '牙', '齿', '种', '子', '杀', '弑', '戮', '游', '泳', '众', '我', '吾', '余', '予', '尔', '汝', '谁', '不', '弗', '肤', '皮', '肉', '肌', '鸟', '禽', '狗', '犬', '羽', '路', '夜', '夕', '晓', '燃', '焚', '燔', '烧', '寡', '绿', '干', '燥', '膏', '脂', '首', '头', '目', '眼', '口', '足', '趾', '脚', '领', '颈', '项', '腹', '根', '啮', '噬', '咬', '步', '执', '持', '秉', '握', '把', '捉', '语', '云', '曰', '谓', '话', '朱', '盈', '满', '良', '吉', '佳', '此', '斯', '兹', '奚', '曷', '咸', '佥', '胥', '俱', '均', '总', '川', '水', '江', '河', '巨', '硕', '树', '木', '止', '停', '息', '住', '忧', '愁', '虑', '昭', '显', '彰', '久', '极', '最', '逸', '入', '始', '初', '肇', '快', '悦', '乐', '喜', '确', '痛', '思', '想', '恭', '敬', '好', '美', '倾', '覆']

    augment_ratio_dic_log = []
    for word in target_chars:
        if word not in already_done_words:
            print(f"word {word} is being processed")
            compiled_dic = compile_each_word_corpus(word, corpus_file_dir)
            compiled_dic = re_assign_timespan(compiled_dic)
            
            if len(compiled_dic[word]) != 7:
                print(word, "语料朝代不全，这可能是由于该字语料太少导致的，请检查。Not all dynasties are in this word's corpus, please check")
            compiled_dic, augment_ratio_dic = augment_corpus_with_target_words(compiled_dic, augmented_sents)
            augment_ratio_dic_log.append(augment_ratio_dic)
            out_dic_filename = f"{compiled_dic_output_dir}/{word}_compiled_corpus.dic"
            with open(out_dic_filename, "wb") as wf:
                p.dump(compiled_dic, wf) 
    
    # log the ratio of added corpus
    # with open("augment_ratio_dic.data", "wb") as wfb:
    #     p.dump(augment_ratio_dic_log, wfb)