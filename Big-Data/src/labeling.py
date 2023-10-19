#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File    :   labeling.py    
@Contact :   2718629413@qq.com
@Software:   PyCharm

@Modify Time      @Author    @Version    @Description
------------      -------    --------    -----------
2022/4/29 10:58      zyz        1.0          None
"""
import numpy as np
from gensim import models, corpora

from label_lda import clean

label = ["maintenance", "bug", "feature", "reliability", "performance"]
reliability_label = ["corruption defense", "annotation", "debug", "robust", "error enhancement"]
performance_label = ["speed optimization", "other", "synchronization", "store optimization", "access optimization"]


def get_label():
    label_file = open("data/labels.txt", "r", encoding='utf-8')
    label_arr = label_file.read().split()
    label_file.close()

    rel_label_file = open("data/reliability_label.txt", "r", encoding='utf-8')
    rel_label_arr = rel_label_file.read().split()
    rel_label_file.close()

    per_label_file = open("data/performance_label.txt", "r", encoding='utf-8')
    per_label_arr = per_label_file.read().split()
    per_label_file.close()

    return label_arr, rel_label_arr, per_label_arr


def gen_list(reliability_list, performance_list):
    reliability = open("data/reliability.txt", "w", encoding='utf-8')
    reliability.write(str(reliability_list).strip('[').strip(']').replace("'", "").replace(',', ''))
    reliability.close()

    performance = open("data/performance.txt", "w", encoding='utf-8')
    performance.write(str(performance_list).strip('[').strip(']').replace("'", "").replace(',', ''))
    performance.close()


def get_list():
    reliability = open("data/reliability.txt", "r", encoding='utf-8')
    reliability_list = reliability.read().split()
    reliability.close()

    performance = open("data/performance.txt", "r", encoding='utf-8')
    performance_list = performance.read().split()
    performance.close()

    return reliability_list, performance_list


def labeling(label_mat, rel_label_mat, per_label_mat, rel_index, per_index):
    for i in range(len(label_mat)):
        content, module = "", ""
        with open("data/" + str(i) + ".txt", "r", encoding='utf-8') as f:
            other_flag, compat_flag = False, False
            line_arr, word_arr = [], []
            for line in f:
                content += line
                line_arr.append(line)
            for word in line_arr:
                word_arr.append(word.split())
            for line in word_arr:
                if len(line) > 0 and line[0] == 'category:':
                    start = 'ipc/'
                    for idx in range(len(line)):
                        if (line[idx] == start + 'util.c' or line[idx] == start + 'msgutil.c' or line[idx]
                            == start + 'util.h' or line[idx] == start + 'Makefile' or line[idx]
                            == start + 'namespace.c' or line[idx] == start + 'syscall.c' or line[idx]
                            == start + 'ipc_sysctl.c' or line[idx]
                            == start + 'mq_sysctl.c') and other_flag is False:
                            module += 'other\t'
                            other_flag = True
                        elif line[idx] == start + 'sem.c':
                            module += 'semaphore\t'
                        elif line[idx] == start + 'shm.c':
                            module += 'shared memory\t'
                        elif line[idx] == start + 'mqueue.c':
                            module += 'message queue\t'
                        elif line[idx] == start + 'msg.c':
                            module += 'message\t'
                        elif (line[idx] == start + 'compat.c' or line[idx]
                              == start + 'compat_mq.c') and compat_flag is False:
                            module += 'compatibility\t'
                            compat_flag = True
        f.close()

        flag = False
        for j in range(len(per_index)):
            if str(i) == per_index[j]:
                content = "label: " + str(label[int(label_mat[i])]) + ' ' + str(
                    performance_label[int(per_label_mat[j])]) + '\n' + \
                          "module: " + module + '\n' + content
                flag = True
                break

        if flag is False:
            for j in range(len(rel_index)):
                if str(i) == rel_index[j]:
                    content = "label: " + str(label[int(label_mat[i])]) + ' ' + str(
                        reliability_label[int(rel_label_mat[j])]) + '\n' + \
                              "module: " + module + '\n' + content
                    flag = True
                    break

        if flag is False:
            content = "label: " + str(label[int(label_mat[i])]) + '\n' + \
                      "module: " + module + '\n' + content

        # print(content)
        file = open("data/" + str(i) + ".txt", "w", encoding='utf-8')
        file.write(content)
        file.close()


def get_data(arr):
    doc = []
    for i in arr:
        content = ""
        with open("data/" + str(i) + ".txt", "r", encoding='utf-8') as f:
            line_arr, word_arr = [], []
            special = ['Link:', 'Cc:', 'Fixes:', 'Acked-by:', 'Signed-off-by:', 'Reviewed-by:', 'Reported-by:',
                       'Co-developed-by:']
            for num, line in enumerate(f):
                if num > 4:
                    line_arr.append(line)
            for word in line_arr:
                word_arr.append(word.split())
            for line in word_arr:
                if len(line) > 0:
                    if line[0] in special:
                        continue
                    else:
                        content += str(line).strip('[').strip(']').replace("'", "").replace(',', "")
        doc.append(content)
        f.close()
    return doc


def process(arr, file_name):
    origin_data = get_data(arr)
    data_clean = [clean(doc).split() for doc in origin_data]
    dictionary = corpora.Dictionary(data_clean)
    corpus = [dictionary.doc2bow(doc) for doc in data_clean]
    lda_model = models.ldamodel.LdaModel
    lda = lda_model(corpus, num_topics=5, id2word=dictionary, passes=15)
    print(lda.print_topics(num_topics=5))

    target = []
    doc_topic = lda.get_document_topics(corpus)
    idx = np.arange(0, len(arr))

    for i in idx:
        topic = np.array(doc_topic[i])
        topic_distribute = np.array(topic[:, 1])
        topic_idx = topic_distribute.argsort()[: -2: -1]
        target.append(topic[topic_idx][0][0])

    target = np.array(target, dtype=np.int)
    file = open("data/" + file_name + ".txt", "w", encoding='utf-8')
    file.write(str(target).strip('[').strip(']').replace("'", ""))
    file.close()


def gen():
    label_file = open("data/labels.txt", "r", encoding='utf-8')
    label_arr = label_file.read().split()
    label_file.close()

    rel_list, per_list = [], []
    for num, item in enumerate(label_arr):
        if int(item) == 3:
            rel_list.append(num)
        elif int(item) == 4:
            per_list.append(num)

    return rel_list, per_list


if __name__ == "__main__":
    # rel_list, per_list = gen()
    # gen_list(rel_list, per_list)
    rel_list, per_list = get_list()
    # process(rel_list, "reliability_label1")
    # process(per_list, "performance_label1")
    label_matrix, rel_label_matrix, per_label_matrix = get_label()
    labeling(label_matrix, rel_label_matrix, per_label_matrix, rel_list, per_list)
