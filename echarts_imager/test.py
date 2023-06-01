from sys import path

path.append('/media/disk2/packages')  # add user packages path to path

from echarts_imager import ECharts

data = {
    "legend": {
        "top": "2%",
        "left": "2%",
        "selectedMode": False,
        "orient": "vertical"
    },
    "series": [{
        "type": "tree",
        "name": "先秦",
        "itemStyle": {
            "color": "#CB1B45"
        },
        "data": [{
            "name":
                "休",
            "children": [{
                "name":
                    "s1-人在树荫下休息",
                "itemStyle": {
                    "color": "#CB1B45"
                },
                "lineStyle": {
                    "color": "#CB1B45"
                },
                "children": [{
                    "name": "s5-休假",
                    "itemStyle": {
                        "color": "#EBB471"
                    },
                    "lineStyle": {
                        "color": "#EBB471"
                    }
                }]
            }, {
                "name":
                    "s2-停止，中止或结束",
                "itemStyle": {
                    "color": "#CB1B45"
                },
                "lineStyle": {
                    "color": "#CB1B45"
                },
                "children": [{
                    "name":
                        "",
                    "itemStyle": {
                        "opacity": 0
                    },
                    "lineStyle": {
                        "color": "#00AA90"
                    },
                    "children": [{
                        "name": "s3-辞去",
                        "itemStyle": {
                            "color": "#00AA90"
                        },
                        "lineStyle": {
                            "color": "#00AA90"
                        }
                    }]
                }, {
                    "name":
                        "s10-勿，莫",
                    "itemStyle": {
                        "color": "#EBB471"
                    },
                    "lineStyle": {
                        "color": "#EBB471"
                    },
                    "children": [{
                        "name": "s8-悠闲，安闲",
                        "itemStyle": {
                            "color": "#00AA90"
                        },
                        "lineStyle": {
                            "color": "#00AA90"
                        }
                    }, {
                        "name":
                            "",
                        "itemStyle": {
                            "opacity": 0
                        },
                        "lineStyle": {
                            "color": "#005CAF"
                        },
                        "children": [{
                            "name": "s4-离弃，解除自己的婚姻",
                            "itemStyle": {
                                "color": "#005CAF"
                            },
                            "lineStyle": {
                                "color": "#005CAF"
                            }
                        }]
                    }, {
                        "name":
                            "",
                        "itemStyle": {
                            "opacity": 0
                        },
                        "lineStyle": {
                            "color": "#005CAF"
                        },
                        "children": [{
                            "name": "s11-罢，了",
                            "itemStyle": {
                                "color": "#005CAF"
                            },
                            "lineStyle": {
                                "color": "#005CAF"
                            }
                        }]
                    }]
                }]
            }, {
                "name":
                    "s6-美善，喜庆",
                "itemStyle": {
                    "color": "#CB1B45"
                },
                "lineStyle": {
                    "color": "#CB1B45"
                },
                "children": [{
                    "name": "s9-盛大，壮大的",
                    "itemStyle": {
                        "color": "#EBB471"
                    },
                    "lineStyle": {
                        "color": "#EBB471"
                    }
                }]
            }, {
                "name": "s7-喜悦的，欢乐的",
                "itemStyle": {
                    "color": "#CB1B45"
                },
                "lineStyle": {
                    "color": "#CB1B45"
                }
            }, {
                "name": "s13-福禄",
                "itemStyle": {
                    "color": "#CB1B45"
                },
                "lineStyle": {
                    "color": "#CB1B45"
                }
            }]
        }],
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
    }, {
        "type": "tree",
        "name": "汉",
        "itemStyle": {
            "color": "#EBB471"
        }
    }, {
        "type": "tree",
        "name": "魏晋六朝",
        "itemStyle": {
            "color": "#00AA90"
        }
    }, {
        "type": "tree",
        "name": "隋唐五代",
        "itemStyle": {
            "color": "#005CAF"
        }
    }]
}

echarts = ECharts(format='svg')
echarts.set_option(data)
echarts.show()
# echarts.format
# echarts.save('test123.png')
