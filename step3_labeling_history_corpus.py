import pickle as p
import numpy as np
from numpy import linalg as la
import torch
from transformers import BertModel, BertTokenizer  #transformers >= 4.0
import glob, os
import numpy as np
from step1_calculate_prototype_sense_embs import get_lastlayer_emb_from_model

'''
根据求得的原型向量，对已去重的语料库中的每个字的每个义项的语料进行标注
去重语料库来自于data/compiled_corpus，是对“语料库在线”中每个字的所有语料进行step0的预处理之后的结果

Using the obtained prototype vector, the corpus of each meaning term of each word in the corpus is labeled
The corpus comes from data/compiled_corpus and is the result of step0 preprocessing of all the corpus for each word in "Corpus Online"

'''

def cosSimilarity(A, B):
    vector1 = np.mat(A)
    vector2 = np.mat(B)
    cosV12 = float(vector1 * vector2.T) / (la.norm(vector1) * la.norm(vector2))
    return cosV12


def tag_sense(emb, sense_d):
    # use the 768d emb to calculate similarity with each sense prototype emb
    result, max_simi = None, 0
    for sk, se in sense_d.items():
        simi = cosSimilarity(emb, se)
        if simi > max_simi:
            result, max_simi = sk, simi
    return result, max_simi


def raw_corpus_tagging(wd, dyna_sents, input_model, sense_protos):
    #input:{dyna1:[sent1,sent2],dyna2:[]}

    tag_results = {}
    for dynasty, sents in dyna_sents.items():
        if dynasty not in tag_results:
            tag_results[dynasty] = []
        for text, book_name in sents:
            if text and text.count(wd) == 1:
                #print(text)
                emb = get_lastlayer_emb_from_model(text, wd, input_model, tokenizer, device)
                predict, similarity = tag_sense(emb, sense_protos[wd])
                tag_results[dynasty].append([text, predict])
        print(f"word {wd} , dynasty {dynasty} has been processed")
    return tag_results


if __name__ == "__main__":

    compiled_dic_dir = "data/compiled_corpus"
    tagged_output = "output_data/tagged_sents_fullmode"
    if not os.path.exists(tagged_output):
        os.mkdir(tagged_output)

    all_words = ['亡', '氏', '报', '心', '济', '令', '奔', '道', '素', '备', '宗', '文', '私', '勒', '适', '长', '许', '忠', '卒', '责', '要', '即', '生', '虚', '达', '视', '迁', '归', '尽', '诚', '史', '诵', '加', '赤', '求', '佛', '比', '逾', '致', '去', '进', '明', '通', '劝', '仁', '穿', '从', '次', '尚', '解', '下', '病', '微', '兵', '若', '怠', '汉', '征', '谒', '举', '相', '遇', '问', '谦', '末', '短', '完', '委', '时', '工', '修', '凶', '智', '闻', '城', '宾', '立', '坐', '属', '情', '公', '论', '直', '后', '负', '死', '族', '胜', '故', '和', '说', '引', '将', '睡', '鲜', '钱', '徐', '务', '宜', '规', '借', '曾', '多', '恨', '华', '忘', '间', '拔', '患', '熙', '汤', '类', '幼', '仙', '君', '前', '释', '孝', '白', '戚', '欲', '具', '池', '悟', '左', '义', '克', '却', '少', '幸', '日', '固', '讽', '暴', '黑', '内', '怨', '旁', '灵', '喻', '敝', '图', '退', '率', '朴', '畜', '化', '育', '遂', '假', '休', '走', '卧', '玉', '老', '为', '笃', '见', '乃', '知', '发', '临', '得', '寐', '冲', '姓', '师', '太', '谢', '博', '大', '王', '乘', '本', '读', '潜', '殆', '奇', '礼', '德', '今', '国', '期', '偃', '涕', '倍', '阴', '会', '或', '念', '中', '何', '璞', '制', '事', '朝', '莫', '夺', '至', '善', '夏', '能', '眠', '出', '稍', '绝', '看', '当', '意', '里', '慕', '寝', '竟', '存', '如', '按', '上', '复', '敌', '既', '识', '处', '陵', '质', '币', '请', '胡', '数', '除', '鄙', '望', '诣', '作', '爱', '就', '诸', '造', '过', '使', '趋', '饯', '非', '籍', '未', '判', '秀', '自', '居', '性', '及', '行', '堪', '贻', '省', '弛', '孰', '教', '紫', '青', '恶', '任', '传', '著', '门', '弥', '名', '山', '清', '神', '书', '安', '贼', '黄', '易', '穷', '兴', '度', '涉', '言', '静', '阳', '信', '振', '辞', '遗', '伪', '方', '疾', '察', '俾', '虞', '延', '红', '家', '被', '泪', '怜', '益', '治', '是', '第', '来', '正', '儒', '置', '理', '与', '而', '让', '便', '徒', '顺', '元', '右', '悉', '顾', '节', '徙', '泅', '肪', '嘴', '肚', '皆', '疼', '亮', '男', '夫', '彼', '女', '妇', '毛', '牙', '齿', '种', '子', '杀', '弑', '戮', '游', '泳', '众', '我', '吾', '余', '予', '尔', '汝', '谁', '不', '弗', '肤', '皮', '肉', '肌', '鸟', '禽', '狗', '犬', '羽', '路', '夜', '夕', '晓', '燃', '焚', '燔', '烧', '寡', '绿', '干', '燥', '膏', '脂', '首', '头', '目', '眼', '口', '足', '趾', '脚', '领', '颈', '项', '腹', '根', '啮', '噬', '咬', '步', '执', '持', '秉', '握', '把', '捉', '语', '云', '曰', '谓', '话', '朱', '盈', '满', '良', '吉', '佳', '此', '斯', '兹', '奚', '曷', '咸', '佥', '胥', '俱', '均', '总', '川', '水', '江', '河', '巨', '硕', '树', '木', '止', '停', '息', '住', '忧', '愁', '虑', '昭', '显', '彰', '久', '极', '最', '逸', '入', '始', '初', '肇', '快', '悦', '乐', '喜', '确', '痛', '思', '想', '恭', '敬', '好', '美', '倾', '覆']

    for f in glob.glob(compiled_dic_dir + "/*.dic"):
        w = os.path.split(f)[-1][0]
        all_words.append(w)
    already_done = glob.glob(tagged_output + "/*")
    already_done_words = []
    for f in already_done:
        already_done_words.append(os.path.split(f)[-1][-5])
    print("already_done_words", already_done_words)

    not_done_yet = list(set(all_words) - set(already_done_words))
    print(not_done_yet)

    #call gpu
    os.environ["CUDA_VISIBLE_DEVICES"] = "2"
    if torch.cuda.is_available():
        device = torch.device("cuda")
        print('There are %d GPU(s) available.' % torch.cuda.device_count())
    else:
        print('No GPU available, using the CPU instead.')
        device = torch.device("cpu")
    tokenizer = BertTokenizer(vocab_file='/siku-simp-bert/vocab.txt')

    #load BERT model
    PRE_TRAINED_MODEL_NAME = "/siku-simp-bert"
    model = BertModel.from_pretrained(PRE_TRAINED_MODEL_NAME)
    model = model.to(device)
    model.eval()
    print("model loaded")

    for word in not_done_yet:
        # if word not in already_done_words:
        compiled_rawdata_filename = f"{compiled_dic_dir}/{word}_compiled_corpus.dic"
        
        with open(compiled_rawdata_filename, "rb") as raw_f:
            word_corpus_dic = p.load(raw_f)

        proto_dir = f"output_data/sense_prototypes_fullmode/{word}_prototypes.dic"
        with open(proto_dir, 'rb') as sensef: 
            sense_protos = p.load(sensef)

        dyna_sents = word_corpus_dic[word]
        tagged_sents = raw_corpus_tagging(word, dyna_sents, model, sense_protos)
        with open(f"{tagged_output}/tagged_sents_{word}.dic", "wb") as wf:
            p.dump(tagged_sents, wf)
