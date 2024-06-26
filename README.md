
# 古汉语词义标注语料库 Ancient Chinese Corpus with Word Sense Annotation
github项目名称：ancient_chinese_sense_annotation

## 简介
古汉语以单音节词为主，其一词多义现象十分突出，这为现代人理解古文含义带来了一定的挑战。为了更好地实现古汉语词义的分析和判别，本研究基于传统辞书和语料库反映的语言事实，设计了针对古汉语多义词的词义划分原则，并对常用古汉语单音节词进行词义级别的知识整理，据此对包含多义词的语料开展词义标注。现阶段语料库共涉及315个单音节词，包含5.8万条标注数据。标注语料来源于“语料库在线”古代汉语语料库(国家语委语料库)和CCL古代汉语语料库，对语料所属时代进行平衡采样，且语料均为简体。

本项目得到国家自然科学基金青年项目“面向古籍整理智能化的知识表示与加工研究（62006021）”资助，由北京师范大学中文信息处理研究所主持开展。
<br>

## 目录
=================
  * [项目特色](#项目特色)
  * [语料库字段介绍](#语料库字段介绍)
  * 实验代码
  * [引用](#引用)


<br/>

## 项目特色
ancient_chinese_sense_annotation有如下几方面优势:
- __义项划分兼顾概括性、时代性和涵盖性__ 词义标注语料库中的义项设立，既需要尊重辞书描写，也需要考虑语言事实和后续信息处理加工的需要。同时，古汉语词汇在数千年的使用中，产生了极为丰富的引申、活用、借用等现象。因此，本项目结合《王力古汉语字典》和《汉语大字典》构建基础词义知识库，兼顾了概括性、时代性和涵盖性，能有效应对古汉语的词义描写时间跨度大、复杂性高等特点，满足词义标注语料库的需要。
- __兼顾同形词的独立性__  如今的很多“同形词”在古代汉语中实际上由不同的古代词形表示，只是受到汉字简化的影响而变成了今天在简化字书写范畴下的“古汉语同形词"。以“后”为例， 根据辞书记载，“后”这个字形共对应了2个同形词，在字形栏分别用“后1”、“后2”标注，词语id栏则用词语序号+字形序号标注。特别地，在同形词各自的义项编号前，由一位数字来区分同形词。
- __对专有名词的特殊标记__ 在实际语料标注中，发现不少词例为专有名词。绝大部分做专名的用法并未被传统辞书收录，而使用频次却相当可观。为了服务于后续的语言学及信息处理研究，本语料库对专有名词单独设立义项编号:s0。具体专名标注规则如下表所示：
```
专有名词类型 义项编号 
人名        s0-1
地名        s0-2 
官名        s0-3 
年号        s0-4
机构名      s0-5 
其他专名    s0-6
```

## 语料库字段介绍
ancient_chinese_sense_annotation的主体分为义项表和语料库。现分别对两表做详细说明。

义项表的格式如下：
```
词语id    词形     义项_id        读音        词性        义项           王力义族            示例       频次
w1        爱        s1        汉语拼音        名        义项描述1        1.0（本义）         例句1       88
w1        爱        s2        汉语拼音        动        义项描述2        1.1（近引申义）     例句2       24   
w1        爱        s3        汉语拼音        形        义项描述3        1.2（近引申义）     例句3       51 
```


语料库的格式如下：
```
词语id    词形      义项描述        语料        义项_id 
w1        爱       义项描述1       句子1           s1  
w1        爱       义项描述2       句子2           s1
w1        爱       义项描述3       句子3           s2
```

## 实验代码

### tensorflow版（论文中使用）
1. 开启bert_service(建议使用nohup后台挂起)

bert-serving-start \
    -pooling_strategy NONE \
    -max_seq_len 128 \
    -pooling_layer -1 \
    -device_map 0 \
    -model_dir siku_bert_tf \
    -show_tokens_to_client \
    -priority_batch_size 32 

2. 获取向量
python3 get_token_emb.py
- 运行该文件，直接读取./data中的EXCEL文件，经预处理滤除不规范的数据后，向bert_service请求向量
- 将目标词的embedding信息以pickle形式保存

3. 词义标注实验
python3 experiment.py threshold
- threshold为阈值，可以在此自行调整，比如取5，则代表仅实验例句数>=5的义项
- 实验结果有两份，statistics文件为每个词实验时涉及的例句、义项数量等信息，tag_result文件为标注结果

### pytorch版（更简单）

python3 get_token_emb_torch.py

python3 experiment.py threshold


## 引用
```
@inproceedings{shu-etal-2021-gu,
    title = "古汉语词义标注语料库的构建及应用研究(The Construction and Application of {A}ncient {C}hinese Corpus with Word Sense Annotation)",
    author = "Shu, Lei  and
      Guo, Yiluan  and
      Wang, Huiping  and
      Zhang, Xuetao  and
      Hu, Renfen",
    booktitle = "Proceedings of the 20th Chinese National Conference on Computational Linguistics",
    month = aug,
    year = "2021",
    address = "Huhhot, China",
    publisher = "Chinese Information Processing Society of China",
    url = "https://aclanthology.org/2021.ccl-1.50",
    pages = "549--563",
    abstract = "{``}古汉语以单音节词为主,其一词多义现象十分突出,这为现代人理解古文含义带来了一定的挑战。为了更好地实现古汉语词义的分析和判别,本研究基于传统辞书和语料库反映的语言事实,设计了针对古汉语多义词的词义划分原则,并对常用古汉语单音节词进行词义级别的知识整理,据此对包含多义词的语料开展词义标注。现有的语料库包含3.87万条标注数据,规模超过117.6万字,丰富了古代汉语领域的语言资源。实验显示,基于该语料库和BERT语言模型,词义判别算法准确率达到80{\%}左右。进一步地,本文以词义历时演变分析和义族归纳为案例,初步探索了语料库与词义消歧技术在语言本体研究和词典编撰等领域的应用。{''}",
    language = "Chinese",
}

```

本文所使用的古汉语四库全书BERT下载地址：

pytorch版：
百度网盘
https://pan.baidu.com/s/1c2WTjJbV4yIGIzQkDB08nw 
提取码：7h3o

tensorflow版：
链接：https://pan.baidu.com/s/1EnZmh2G7mflzRvf6Wck2EA?pwd=e87j 
提取码：e87j

