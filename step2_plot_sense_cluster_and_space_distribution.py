import pickle as p
import os
import re
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
from mpl_toolkits import mplot3d
import glob
import matplotlib as mpl
import scipy.cluster.hierarchy as sch
from matplotlib.font_manager import fontManager


def plot_cluster(word, emb_dic_per_word):
    """
    对每个词的多个义项的原型向量做层次聚类
    Hierarchical clustering of prototype vectors of multiple senses for each word
    """
    try:
        senses_sorted = sorted(
            emb_dic_per_word.items(),
            key=lambda x: (
                "".join(re.findall("^\d+", x[0])),
                int(re.findall("s\d+", x[0])[0][1:]),
                x[0],
            ),
        )  # 按照义项编号排序
    except:
        senses_sorted = sorted(emb_dic_per_word.items(), key=lambda x: x[0])

    emb_dic_per_word = dict(senses_sorted)
    emb_lst = []
    for sense, vec in emb_dic_per_word.items():
        cur_sense = []
        cur_sense.append(sense)
        for i in vec:
            cur_sense.append(i)
        emb_lst.append(cur_sense)

    df = pd.DataFrame(emb_lst)

    plt.figure(figsize=(10, 8))
    """
    生成点与点之间的距离矩阵disMat, 使用欧氏距离: euclidean
    X：聚类对象
    Generate a distance matrix disMat between points, using Euclidean distance: euclidean
    X: Cluster objects
    """
    disMat = sch.distance.pdist(X=df.iloc[:, 1:], metric="cosine")

    # 进行层次聚类: 簇间距离计算的方法使用 ward 法。 Do hierarchical clustering, use ward as between-cluster distance calculation method

    Z = sch.linkage(disMat, method="ward")  # f
    # 将层级聚类结果以树状图表示出来并保存 Present the hierarchical clustering results as a treemap and save them
    P = sch.dendrogram(Z, labels=list(df.iloc[:, 0]), orientation="left")
    plt.xticks(fontsize=20)
    plt.yticks(fontsize=20)
    plt.savefig(save_dir + "%s层次聚类.png" % word, bbox_inches="tight")


def plot_3dsense_embs(word, emb_dic_per_word):
    """
    画义项三维空间分布图
    Draw a three-dimensional spatial distribution map of senses
    """
    try:
        senses_sorted = sorted(
            emb_dic_per_word.items(),
            key=lambda x: (
                "".join(re.findall("^\d+", x[0])),
                int(re.findall("s\d+", x[0])[0][1:]),
                x[0],
            ),
        )
    except:
        senses_sorted = sorted(emb_dic_per_word.items(), key=lambda x: x[0])
    emb_dic_per_word = dict(senses_sorted)
    senses = list((emb_dic_per_word.keys()))

    emb_lst = []
    for sense, vec in emb_dic_per_word.items():
        cur_sense = []
        cur_sense.append(sense)
        for i in vec:
            cur_sense.append(i)
        emb_lst.append(cur_sense)
    emb_lst = sorted(emb_lst, key=lambda x: x[0][1])
    df = pd.DataFrame(emb_lst)
    # print(df)
    X = df.iloc[:, 1:]
    # PCA
    pca_sk = PCA(n_components=3)
    newMat = pca_sk.fit_transform(X)
    x = newMat[:, 0]
    y = newMat[:, 1]
    z = newMat[:, 2]

    plt.figure(figsize=(20, 16))
    ax = plt.axes(projection="3d")
    # plt.rc('font', **{'family': font_name})
    plt.rcParams["axes.unicode_minus"] = False
    colors = ["k", "g", "r", "y", "b", "m", "#00CED1"]
    markers = ["^", "+", "o", "D", ".", "*", "s", "h"]
    txt = list(df.iloc[:, 0])
    color_idx = 0

    for i, sense in enumerate(senses):
        # find the position from x,y,z aspects
        sense_idx = []
        x_sense = []
        y_sense = []
        z_sense = []
        for idx, line in enumerate(txt):
            if line == sense:
                sense_idx.append(idx)
                x_sense.append(x[idx])
                y_sense.append(y[idx])
                z_sense.append(z[idx])
        x_sense = np.array(x_sense)
        y_sense = np.array(y_sense)
        z_sense = np.array(z_sense)

        ax.scatter(
            x_sense,
            y_sense,
            z_sense,
            s=400,
            marker=markers[color_idx % len(markers)],
            c=colors[color_idx % len(colors)],
            label=sense,
        )
        color_idx += 1

        box = ax.get_position()
        ax.set_position([box.x0, box.y0, box.width, box.height])
        ax.legend(bbox_to_anchor=(1.04, 1), prop={"size": 40}, borderaxespad=0)
    plt.savefig(save_dir + "%s语义空间.png" % word, bbox_inches="tight")
    plt.show()


def get_3d_slices(word, emb_dic_per_word):
    """
    一张静态的三维图还不足以看清楚各个点之间的距离关系
    从x,y,z三个方向观察这张三维空间图，输出三个二维截面

    A static 3D plot is not enough to see the distance between points
    This three-dimensional space diagram is observed from the three directions of x, y, and z, and three two-dimensional sections are the output
    """
    emb_lst = []
    for sense, vec in embs.items():
        cur_sense = []
        cur_sense.append(sense)
        for i in vec:
            cur_sense.append(i)
        emb_lst.append(cur_sense)

    df = pd.DataFrame(emb_lst)

    X = df.iloc[:, 1:]

    # 降维
    pca_sk = PCA(n_components=3)
    newMat = pca_sk.fit_transform(X)
    senses = list(emb_dic_per_word.keys())
    x = newMat[:, 0]
    y = newMat[:, 1]
    z = newMat[:, 2]

    for without_dim in ["x", "y", "z"]:
        plt.figure(figsize=(10, 10))
        ax = plt.axes()
        plt.xticks(fontsize=20)
        plt.yticks(fontsize=20)
        # plt.rc('font', **{'family': font_name})
        plt.rcParams["axes.unicode_minus"] = False
        colors = ["k", "g", "r", "y", "b", "m", "#00CED1"]
        markers = ["^", "+", "o", "D", ".", "*", "s", "h"]
        txt = list(df.iloc[:, 0])
        color_idx = 0
        for i, sense in enumerate(senses):
            # 找出所有属于这个意义的x,text
            sense_idx = []
            x_sense = []
            y_sense = []
            z_sense = []
            for idx, line in enumerate(txt):
                if line == sense:
                    sense_idx.append(idx)
                    x_sense.append(x[idx])
                    y_sense.append(y[idx])
                    z_sense.append(z[idx])
            x_sense = np.array(x_sense)
            y_sense = np.array(y_sense)
            z_sense = np.array(z_sense)

            if without_dim == "x":
                ax.scatter(
                    y_sense,
                    z_sense,
                    s=400,
                    marker=markers[color_idx % len(markers)],
                    c=colors[color_idx % len(colors)],
                    label=sense,
                )
                plt.xlabel("dim2", fontsize=30)
                plt.ylabel("dim3", fontsize=30)
                color_idx += 1
                box = ax.get_position()
                ax.set_position([box.x0, box.y0, box.width, box.height])
                ax.legend(
                    loc=2,
                    bbox_to_anchor=(1.05, 1.0),
                    borderaxespad=0.0,
                    prop={"size": 40},
                )

            if without_dim == "y":
                ax.scatter(
                    x_sense,
                    z_sense,
                    s=400,
                    marker=markers[color_idx % len(markers)],
                    c=colors[color_idx % len(colors)],
                    label=sense,
                )
                plt.xlabel("dim1", fontsize=30)
                plt.ylabel("dim3", fontsize=30)
                color_idx += 1
                print(sense)
                box = ax.get_position()
                ax.set_position([box.x0, box.y0, box.width, box.height])
                ax.legend(
                    loc=2,
                    bbox_to_anchor=(1.05, 1.0),
                    borderaxespad=0.0,
                    prop={"size": 40},
                )
            if without_dim == "z":
                ax.scatter(
                    x_sense,
                    y_sense,
                    s=400,
                    marker=markers[color_idx % len(markers)],
                    c=colors[color_idx % len(colors)],
                    label=sense,
                )
                plt.xlabel("dim1", fontsize=30)
                plt.ylabel("dim2", fontsize=30)
                color_idx += 1
                print(sense)
                box = ax.get_position()
                ax.set_position([box.x0, box.y0, box.width, box.height])
                ax.legend(
                    loc=2,
                    bbox_to_anchor=(1.05, 1.0),
                    borderaxespad=0.0,
                    prop={"size": 40},
                )
        plt.savefig(
            save_dir + "%s语义空间切片%s.png" % (word, without_dim), bbox_inches="tight"
        )


if __name__ == "__main__":
    plt.rcParams["axes.unicode_minus"] = False
    song_path = "utils/simsun.ttf"
    fontManager.addfont(song_path)
    prop = mpl.font_manager.FontProperties(fname=song_path)
    mpl.rcParams["font.family"] = prop.get_name()
    save_dir = "义项空间分布_fullmode/"
    prototypes_dir = "output_data/sense_prototypes_fullmode/"

    # visualization pipeline of each word's senses
    for f in glob.glob(prototypes_dir + "*.dic"):
        with open(f, "rb") as pkf:
            word = os.path.split(f)[-1][0]

            prototype_emb_dic = p.load(pkf)
            embs = prototype_emb_dic[word]

            try:
                plot_cluster(word, embs)
                print("plotted:", word)
            except ValueError:
                print("not plotted:", word)
                pass

            try:
                plot_3dsense_embs(word, embs)
            except ValueError:
                print("not plotted:", word)
                pass
            try:
                get_3d_slices(word, embs)
            except ValueError:
                print("not plotted:", word)
                pass
