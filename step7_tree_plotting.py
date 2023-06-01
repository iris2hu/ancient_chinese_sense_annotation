from sys import path

from echarts_imager import ECharts

import json
import pickle as p


words = ['亡', '氏', '报', '心', '济', '令', '奔', '道', '素', '备', '宗', '文', '私', '勒', '适', '长', '许', '忠', '卒', '责', '要', '即', '生', '虚', '达', '视', '迁', '归', '尽', '诚', '史', '诵', '加', '赤', '求', '佛', '比', '逾', '致', '去', '进', '明', '通', '劝', '仁', '穿', '从', '次', '尚', '解', '下', '病', '微', '兵', '若', '怠', '汉', '征', '谒', '举', '相', '遇', '问', '谦', '末', '短', '完', '委', '时', '工', '修', '凶', '智', '闻', '城', '宾', '立', '坐', '属', '情', '公', '论', '直', '后', '负', '死', '族', '胜', '故', '和', '说', '引', '将', '睡', '鲜', '钱', '徐', '务', '宜', '规', '借', '曾', '多', '恨', '华', '忘', '间', '拔', '患', '熙', '汤', '类', '幼', '仙', '君', '前', '释', '孝', '白', '戚', '欲', '具', '池', '悟', '左', '义', '克', '却', '少', '幸', '日', '固', '讽', '暴', '黑', '内', '怨', '旁', '灵', '喻', '敝', '图', '退', '率', '朴', '畜', '化', '育', '遂', '假', '休', '走', '卧', '玉', '老', '为', '笃', '见', '乃', '知', '发', '临', '得', '寐', '冲', '姓', '师', '太', '谢', '博', '大', '王', '乘', '本', '读', '潜', '殆', '奇', '礼', '德', '今', '国', '期', '偃', '涕', '倍', '阴', '会', '或', '念', '中', '何', '璞', '制', '事', '朝', '莫', '夺', '至', '善', '夏', '能', '眠', '出', '稍', '绝', '看', '当', '意', '里', '慕', '寝', '竟', '存', '如', '按', '上', '复', '敌', '既', '识', '处', '陵', '质', '币', '请', '胡', '数', '除', '鄙', '望', '诣', '作', '爱', '就', '诸', '造', '过', '使', '趋', '饯', '非', '籍', '未', '判', '秀', '自', '居', '性', '及', '行', '堪', '贻', '省', '弛', '孰', '教', '紫', '青', '恶', '任', '传', '著', '门', '弥', '名', '山', '清', '神', '书', '安', '贼', '黄', '易', '穷', '兴', '度', '涉', '言', '静', '阳', '信', '振', '辞', '遗', '伪', '方', '疾', '察', '俾', '虞', '延', '红', '家', '被', '泪', '怜', '益', '治', '是', '第', '来', '正', '儒', '置', '理', '与', '而', '让', '便', '徒', '顺', '元', '右', '悉', '顾', '节', '徙', '泅', '肪', '嘴', '肚', '皆', '疼', '亮', '男', '夫', '彼', '女', '妇', '毛', '牙', '齿', '种', '子', '杀', '弑', '戮', '游', '泳', '众', '我', '吾', '余', '予', '尔', '汝', '谁', '不', '弗', '肤', '皮', '肉', '肌', '鸟', '禽', '狗', '犬', '羽', '路', '夜', '夕', '晓', '燃', '焚', '燔', '烧', '寡', '绿', '干', '燥', '膏', '脂', '首', '头', '目', '眼', '口', '足', '趾', '脚', '领', '颈', '项', '腹', '根', '啮', '噬', '咬', '步', '执', '持', '秉', '握', '把', '捉', '语', '云', '曰', '谓', '话', '朱', '盈', '满', '良', '吉', '佳', '此', '斯', '兹', '奚', '曷', '咸', '佥', '胥', '俱', '均', '总', '川', '水', '江', '河', '巨', '硕', '树', '木', '止', '停', '息', '住', '忧', '愁', '虑', '昭', '显', '彰', '久', '极', '最', '逸', '入', '始', '初', '肇', '快', '悦', '乐', '喜', '确', '痛', '思', '想', '恭', '敬', '好', '美', '倾', '覆']

time_series = {"清至民初":6,"元明":5,"宋":4,"隋唐五代":3, "魏晋六朝":2, "汉":1, "先秦":0}
color_series = {"清至民初":"#65318e","元明":"#19448e","宋":"#007bbb","隋唐五代":"#00AA90", "魏晋六朝":"#ffea00", "汉":"#f08300", "先秦":"#CB1B45"}

def construct_default_tree(word):
    '''
    树形图的默认设置
    '''
    ori_dict = {
        "legend": {
          "top": "2%",
          "left": "2%",
          "selectedMode": False,
          "orient": "vertical"
        },
        "series": [
          {
            "type": "tree",
            "name": "先秦",
            "itemStyle": {
              "color": "#CB1B45"
            },
            "data": [{
                "name": f"{word}",
                "children": []}],
            "top": "1%",
            "left": "7%",
            "bottom": "1%",
            "right": "20%",
            "symbolSize": 10,
            "label": {
              "position": "left",
              "verticalAlign": "middle",
              "align": "right",
              "fontSize": 15
            },
            "leaves": {
              "label": {
                "position": "right",
                "verticalAlign": "middle",
                "align": "left"
              }
            },
            "expandAndCollapse": False
          },
          {
            "type": "tree",
            "name": "汉",
            "itemStyle": {
              "color": "#f08300"
            }
          },
          {
            "type": "tree",
            "name": "魏晋六朝",
            "itemStyle": {
              "color": "#ffea00"
            }
          },
          {
            "type": "tree",
            "name": "隋唐五代",
            "itemStyle": {
              "color": "#00AA90"
            }
          },
          {
            "type": "tree",
            "name": "宋",
            "itemStyle": {
              "color": "#007bbb"
            }
          },
          {
            "type": "tree",
            "name": "元明",
            "itemStyle": {
              "color": "#19448e"
            }
          },
          {
            "type": "tree",
            "name": "清至民初",
            "itemStyle": {
              "color": "#65318e"
            }
          }
        ]
      }
    return ori_dict

for word in words:
    all_items = {}
    with open(f"output_data/chained_results_fullmode/{word}chained_senses.dic", "rb")as pkf:
        chained_dic = p.load(pkf)
    for sense, info in chained_dic.items():
        if info.get('emerge_time'):
          color = color_series[info.get('emerge_time')]
          each_sense = {
                  "name": sense,
                  "itemStyle": {
                  "color": color
                  },
                  "lineStyle": {
                  "color": color
                  },
                  "children": []}
          all_items[sense] = each_sense
    #把childern填进去
    for dynasty in ["清至民初","元明","宋","隋唐五代", "魏晋六朝", "汉", "先秦"]: #从后往前合并
        for sense, info in chained_dic.items():
            if info.get('emerge_time') and info['emerge_time'] == dynasty:
                if info['from'] and info['from'] != sense:
                    from_time = chained_dic[info['from']].get('emerge_time')
                    if from_time:
                      cur_item = all_items[sense]
                      cur_color = color_series[info['emerge_time']]
                      depth = time_series[info['emerge_time']] - time_series[from_time]
                      for _ in range(depth-1):
                          dummy = {
                          "name": "",
                          "itemStyle": {
                              "opacity": 0
                          },
                          "lineStyle": {
                              "color": cur_color
                          },
                          "children": [
                          ]
                          }
                          dummy["children"].append(cur_item)
                          cur_item = dummy
                      all_items[info['from']]['children'].append(cur_item)
                      all_items.pop(sense)
            
        

    written = set()
    char_tree = construct_default_tree(word)
    for sense, dict in all_items.items():
        if sense not in written:
            print("write sense", sense)
            char_tree["series"][0]['data'][0]['children'].append(dict)
        written.add(sense)

    chart = ECharts(char_tree, format="png", size=(1000, 600), device_pixel_ratio=2)
    chart.save(path=f"output_data/chained_results_fullmode/{word}_词义引申树.png")