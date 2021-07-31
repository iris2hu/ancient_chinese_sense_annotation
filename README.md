# ancient_chinese_sense_annotation
Ancient Chinese Corpus with Word Sense Annotation

古汉语以单音节词为主，其一词多义现象十分突出，这为现代人理解古文含义带来了一定的挑战。为了更好地实现古汉语词义的分析和判别，本研究基于传统辞书和语料库反映的语言事实，设计了针对古汉语多义词的词义划分原则，并对常用古汉语单音节词进行词义级别的知识整理，据此对包含多义词的语料开展词义标注。现阶段语料库共涉及200个单音节词，包含45万条标注数据。标注语料来源于“语料库在线”古代汉语语料库(国家语委语料库)和CCL古代汉语语料库，对语料所属时代进行平衡采样，且语料均为简体。

<br>

目录
=================
  * [项目特色](#项目特色)
  * [语料库字段介绍](#语料库字段介绍)
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
机构名        s0-5 
其他专名        s0-6
```

## 语料库字段介绍
ancient_chinese_sense_annotation的主体分为义项表和语料库。现分别对两表做详细说明。
义项表
义项表的格式如下：
```
词语id    词形     义项_id        读音        词性        义项           王力义族            示例       频次
w1        爱        s1        汉语拼音        名        义项描述1        1.0（本义）         例句1       88
w1        爱        s2        汉语拼音        动        义项描述2        1.1（近引申义）     例句2       24   
w1        爱        s3        汉语拼音        形        义项描述3        1.2（近引申义）     例句3       51 
```

语料库
语料库的格式如下：
```
词语id    词形      义项描述        语料        义项_id 
w1        爱       义项描述1       句子1           s1  
w1        爱       义项描述2       句子2           s1
w1        爱       义项描述3       句子3           s2
```


## 引用
```
@inproceedings{lei-etal-2021,
    title = "古汉语词义标注语料库的构建及应用研究",
    author = "Lei Shu, Yiluan Guo, Huiping Wang, Xuetao Zhang and Renfen Hu",
    booktitle = "Proceedings of the 20th Chinese National Conference on Computational Linguistics",
    month = oct,
    year = "2021",
    address = "Hohhot, China",
    publisher = "Chinese Information Processing Society of China",
    language = "Chinese",
}
```
