#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File    :   ploting.py    
@Contact :   2718629413@qq.com
@Software:   PyCharm

@Modify Time      @Author    @Version    @Description
------------      -------    --------    -----------
2022/4/30 15:48      zyz        1.0          None
"""
import csv
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import ticker
from matplotlib import cm

labels, modules, ages, versions, lines = [], [], [], ["" for _ in range(874)], []
module_labels = ["other", "semaphore", "shared memory", "message queue", "message", "compatibility"]
patch_type = ["Bug", "Maintenance", "Feature", "Performance", "Reliability"]
reliability_label = ["corruption defense", "annotation", "debug", "robust", "error enhancement"]
performance_label = ["speed optimization", "other", "synchronization", "store optimization", "access optimization"]
version_labels = ["v2.x", "v3.x", "v4.x", "v5.x"]
bug_pattern_labels = ['Semantic', 'Concurrency', 'Memory', 'errorCode']
consequences_labels = ['Corruption', 'Crash', 'Error', 'Deadlock', 'Leak', 'Wrong', 'Hang']
bug_patterns, consequences = [], []
title = []
minus, plus = [], []


def get_data():
    for i in range(874):
        flag = False
        with open("data/" + str(i) + ".txt", "r", encoding='utf-8') as f:
            for num, line in enumerate(f):
                content = line.split()
                if num == 0 and str(content[1]) == 'bug':
                    flag = True
                if num == 0:
                    if flag:
                        for item in bug_pattern_labels:
                            if str(content[2]) == item or str(content[2]) == item.lower():
                                bug_patterns.append(item)
                                break
                    else:
                        bug_patterns.append("")
                        consequences.append("")
                    labels.append(content[1:])
                elif (flag is False and num == 1) or (flag and num == 2):
                    j = 1
                    module = []
                    while j < len(content):
                        if j + 1 < len(content):
                            if str(content[j] + " " + content[j + 1]) in module_labels:
                                module.append(str(content[j] + " " + content[j + 1]))
                                j += 2
                            else:
                                if str(content[j]) in module_labels:
                                    module.append(str(content[j]))
                                    j += 1
                        else:
                            if str(content[j]) in module_labels:
                                module.append(str(content[j]))
                                j += 1
                    modules.append(module)
                elif (flag is False and num == 2) or (flag and num == 3):
                    ages.append(content[1:])
                elif (flag is False and num == 3) or (flag and num == 4):
                    title.append(str(line).strip("title: ").strip('\n'))
                elif (flag is False and num == 5) or (flag and num == 6):
                    pos = int(str(content[1:][0]).split('/')[1])
                    neg = int(str(content[1:][0]).split('/')[0])
                    minus.append(neg)
                    plus.append(pos)
                    lines.append(abs(pos - neg))
                elif flag and num == 1:
                    if len(content) > 1:
                        consequences.append(str(content[1]))
                    else:
                        consequences.append(str(content)[str(content).find('：') + 1:].replace("'", "").replace("]", ""))
                else:
                    continue

    f.close()


def get_module_patch_types_data():
    results = {
        'other': [0 for _ in range(5)],
        'semaphore': [0 for _ in range(5)],
        'shared memory': [0 for _ in range(5)],
        'message queue': [0 for _ in range(5)],
        'message': [0 for _ in range(5)],
        'compatibility': [0 for _ in range(5)]
    }

    for idx in range(len(modules)):
        row, col = 0, 0
        module = modules[idx]
        patch = labels[idx][0]

        for i in range(len(patch_type)):
            if patch == patch_type[i].lower():
                col = i
                if col == 1:
                    col = 2
                elif col == 2:
                    col = 1
                break

        for i in range(len(module)):
            module_label = module[i]
            for j in range(len(module_labels)):
                if module_label == module_labels[j]:
                    results[module_label][col] += 1
                    break

    return results


def get_module_performance_data(label):
    results = {
        'other': [0],
        'semaphore': [0],
        'shared memory': [0],
        'message queue': [0],
        'message': [0],
        'compatibility': [0]
    }

    for idx in range(len(modules)):
        module = modules[idx]
        patch = labels[idx][0]

        if patch != label:
            continue

        for i in range(len(module)):
            module_label = module[i]
            for j in range(len(module_labels)):
                if module_label == module_labels[j]:
                    results[module_label][0] += 1
                    break

    return results


def get_module_performance_details_data(label):
    results = {
        'other': [0 for _ in range(len(performance_label))],
        'semaphore': [0 for _ in range(len(performance_label))],
        'shared memory': [0 for _ in range(len(performance_label))],
        'message queue': [0 for _ in range(len(performance_label))],
        'message': [0 for _ in range(len(performance_label))],
        'compatibility': [0 for _ in range(len(performance_label))]
    }

    for idx in range(len(modules)):
        col = 0
        module = modules[idx]
        patch = labels[idx][0]

        if patch != label:
            continue

        if patch == label:
            p_type = str(labels[idx][1:]).strip('[').strip(']').replace("'", "").replace(',', '')
            for i in range(len(performance_label)):
                if label == "performance":
                    if p_type == performance_label[i].lower():
                        col = i
                        break
                else:
                    if p_type == reliability_label[i].lower():
                        col = i
                        break

        for i in range(len(module)):
            module_label = module[i]
            for j in range(len(module_labels)):
                if module_label == module_labels[j]:
                    results[module_label][col] += 1
                    break

    return results


def get_version_patch_types_data():
    results = {
        'v2.x': [0 for _ in range(5)],
        'v3.x': [0 for _ in range(5)],
        'v4.x': [0 for _ in range(5)],
        'v5.x': [0 for _ in range(5)],
    }

    for idx in range(len(versions)):
        row, col = 0, 0
        version = versions[idx]
        patch = labels[idx][0]

        for i in range(len(patch_type)):
            if patch == patch_type[i].lower():
                col = i
                if col == 1:
                    col = 2
                elif col == 2:
                    col = 1
                break

        for j in range(len(version_labels)):
            if version == version_labels[j]:
                results[version][col] += 1
                break

    return results


def get_lines_patch_types_data():
    results = {
        'v2.x': [0 for _ in range(5)],
        'v3.x': [0 for _ in range(5)],
        'v4.x': [0 for _ in range(5)],
        'v5.x': [0 for _ in range(5)],
    }

    for idx in range(len(versions)):
        row, col = 0, 0
        version = versions[idx]
        line = lines[idx]
        patch = labels[idx][0]

        for i in range(len(patch_type)):
            if patch == patch_type[i].lower():
                col = i
                if col == 1:
                    col = 2
                elif col == 2:
                    col = 1
                break

        for j in range(len(version_labels)):
            if version == version_labels[j]:
                results[version][col] += int(line)
                break

    return results


def get_version_bug_pattern_data():
    results = {
        'v2.x': [0 for _ in range(4)],
        'v3.x': [0 for _ in range(4)],
        'v4.x': [0 for _ in range(4)],
        'v5.x': [0 for _ in range(4)],
    }

    for idx in range(len(versions)):
        col = 0
        version = versions[idx]
        pattern = bug_patterns[idx]
        if pattern == '':
            continue

        for j in range(len(bug_pattern_labels)):
            if pattern == bug_pattern_labels[j]:
                col = j
                break

        for j in range(len(version_labels)):
            if version == version_labels[j]:
                results[version][col] += 1
                break

    return results


def get_version_consequences_data():
    results = {
        'v2.x': [0 for _ in range(len(consequences_labels))],
        'v3.x': [0 for _ in range(len(consequences_labels))],
        'v4.x': [0 for _ in range(len(consequences_labels))],
        'v5.x': [0 for _ in range(len(consequences_labels))],
    }

    for idx in range(len(versions)):
        col = 0
        version = versions[idx]
        cons = consequences[idx]

        if cons != '':
            for j in range(len(consequences_labels)):
                if cons == consequences_labels[j].lower():
                    col = j
                    break

            for j in range(len(version_labels)):
                if version == version_labels[j]:
                    results[version][col] += 1
                    break

    return results


def get_consequences_bug_pattern_data():
    results = {
        'Corruption': [0 for _ in range(len(bug_pattern_labels))],
        'Crash': [0 for _ in range(len(bug_pattern_labels))],
        'Error': [0 for _ in range(len(bug_pattern_labels))],
        'Deadlock': [0 for _ in range(len(bug_pattern_labels))],
        'Leak': [0 for _ in range(len(bug_pattern_labels))],
        'Wrong': [0 for _ in range(len(bug_pattern_labels))],
        'Hang': [0 for _ in range(len(bug_pattern_labels))],
    }

    for idx in range(len(consequences)):
        col = 0
        bug_pattern = bug_patterns[idx]
        cons = consequences[idx]

        if cons != '':
            for j in range(len(bug_pattern_labels)):
                if bug_pattern == bug_pattern_labels[j]:
                    col = j
                    break

            for j in range(len(consequences_labels)):
                if cons == consequences_labels[j].lower():
                    results[consequences_labels[j]][col] += 1
                    break

    return results


def get_version_patch_data(types):
    results = {
        'v2.x': [0 for _ in range(5)],
        'v3.x': [0 for _ in range(5)],
        'v4.x': [0 for _ in range(5)],
        'v5.x': [0 for _ in range(5)],
    }

    for idx in range(len(versions)):
        row, col = 0, 0
        version = versions[idx]
        patch = labels[idx][0]

        if patch == types:
            p_type = str(labels[idx][1:]).strip('[').strip(']').replace("'", "").replace(',', '')
            for i in range(5):
                if types == "performance":
                    if p_type == performance_label[i].lower():
                        col = i
                        break
                else:
                    if p_type == reliability_label[i].lower():
                        col = i
                        break

            for j in range(len(version_labels)):
                if version == version_labels[j]:
                    results[version][col] += 1
                    break

    return results


def draw_bar(results, category_names, x_label):
    keys = list(results.keys())
    keys = [item.title() for item in keys]
    category_names = [item.title() for item in category_names]
    data = np.array(list(results.values())).T
    data_cum = np.sum(data, axis=0)
    category_colors=[[0.80392,0.2,0.2,1.        ],
                     [0.93333,0.93333,  0   ,    1.        ],
                     [0.93333, 0.67843, 0.0549, 1.],
                     [0.80392, 0.41176, 0.78824, 1.],
                     [0.41176,0.34902,0.80392,1.        ],
                     [0.23529, 0.70196, 0.44314, 1.],
                     [0.81176,0.81176,0.81176,1.        ]]
    fig, ax = plt.subplots(figsize=(8, 5))

    fontsize = 14
    # if x_label == 'Version':
    #     plt.yticks(fontsize=fontsize)
    #     plt.xticks(fontsize=fontsize)
    ax.set_ylabel("Percentage (%)", fontsize=fontsize)
    # ax.set_xlabel(str(x_label), fontsize=fontsize)

    def to_percent(temp, position):
        return '%1.0f' % (100 * temp)

    ax.yaxis.set_major_formatter(ticker.FuncFormatter(to_percent))

    bottom_y = np.zeros(len(keys))
    for i, (col_name, color) in enumerate(zip(category_names, category_colors)):
        y = data[i] / data_cum
        ax.bar(keys, y, bottom=bottom_y, width=0.5, label=col_name, color=color)
        bottom_y = bottom_y + y

    num1, num2, num3, num4 = 0, 1, 3, 0.5
    # if x_label == 'Version':
    #     ax1 = ax.twinx()
    #     lns_ = ax1.plot(keys, data_cum, linewidth=3, color='grey',label='The Number of Patches')
    #     ax1.set_ylabel('The Number Of Patches', fontsize=fontsize)
    #     handles, labels = ax.get_legend_handles_labels()
    #     handles1, labels1 = ax1.get_legend_handles_labels()
    #     plt.legend(handles=[handles, handles1], bbox_to_anchor=(num1, num2), loc=num3, borderaxespad=num4, ncol=4, fontsize=fontsize)
    # else:
    plt.legend(bbox_to_anchor=(num1, num2), loc=num3, borderaxespad=num4, ncol=3, fontsize=fontsize)
    plt.xticks(rotation=45)

    plt.tick_params(labelsize=fontsize)
    plt.tight_layout()
    plt.savefig(str(x_label) + '.png', dpi=1500, bbox_inches='tight')
    plt.show()


def draw_line(results, x_label):
    keys = np.array(list(results.keys()))
    data = np.array(list(results.values()))
    x = np.arange(2, 6)
    plt.figure(figsize=(8, 5))
    plt.plot(x, data.T[0], label=patch_type[0])
    plt.plot(x, data.T[1], label=patch_type[1])
    plt.plot(x, data.T[2], label=patch_type[2])
    plt.plot(x, data.T[3], label=patch_type[3])
    plt.plot(x, data.T[4], label=patch_type[4])
    fontsize = 14
    plt.xticks(x, keys, fontsize=fontsize)
    plt.yticks(fontsize=fontsize)
    plt.xlabel(x_label, fontsize=fontsize)
    plt.ylabel("Number Of Lines Modified", fontsize=fontsize)
    plt.tight_layout()
    plt.legend(loc="best", fontsize=fontsize)
    plt.savefig("patch.png", dpi=1500, bbox_inches='tight')
    plt.show()


def get_version():
    res = {}
    with open("data/version.txt", "r", encoding='utf-8') as f:
        for line in f:
            res[line.split()[0]] = line.split()[1]
    f.close()
    res = sorted(res.items(), key=lambda x: x[1], reverse=True)

    for num, date in enumerate(ages):
        for data in res:
            if versions[num] != "":
                break
            if str(date[0]) >= str(data[1]):
                versions[num] = str(data[0][:3]) + 'x'
        if versions[num] == "":
            versions[num] = "v2.x"


def draw_trend_line(results):
    keys = np.array(list(results.keys()))
    data = np.array(list(results.values()))
    x = np.arange(2, 6)
    plt.figure(figsize=(8, 5))
    fontsize = 14
    plt.plot(x, data.T[0], label=bug_pattern_labels[0])
    plt.plot(x, data.T[1], label=bug_pattern_labels[1])
    plt.plot(x, data.T[2], label=bug_pattern_labels[2])
    plt.plot(x, data.T[3], label=bug_pattern_labels[3])
    plt.yticks(fontsize=fontsize)
    plt.xticks(x, keys, fontsize=fontsize)
    plt.legend(loc="best", fontsize=fontsize)
    plt.xlabel("Version", fontsize=fontsize)
    plt.ylabel("The Number Of Lines", fontsize=fontsize)
    plt.tight_layout()
    plt.savefig("trend.png", dpi=1500, bbox_inches='tight')
    plt.show()


def draw_module(results, title):
    keys = np.array(list(results.keys()))
    data = np.array(list(results.values())).reshape(-1)
    tot = sum(data)
    data = data / tot
    norm = plt.Normalize(min(data), max(data))
    norm_values = norm(data)
    map_vir = cm.get_cmap(name='coolwarm')
    plt.figure(figsize=(8, 5))
    fontsize = 14
    colors = map_vir(norm_values)
    plt.bar(keys, data, color=colors)
    sm = cm.ScalarMappable(cmap=map_vir, norm=norm)
    sm.set_array([])
    plt.colorbar(sm)
    plt.xticks(rotation=45, fontsize=fontsize)
    plt.yticks([0, 0.05, 0.10, 0.15, 0.20, 0.25], ["0%", "5%", "10%", "15%", "20%", "25%"], fontsize=fontsize)
    plt.ylabel("Percentage (%)", fontsize=fontsize)
    # plt.xlabel(title, fontsize=fontsize)
    plt.tick_params(labelsize=fontsize)
    plt.tight_layout()
    plt.savefig(title + '.png', dpi=1500, bbox_inches='tight')
    plt.show()


def txt2csv():
    file = open("data.csv", "w", encoding='utf-8', newline='')
    csv_writer = csv.writer(file)
    for i in range(len(labels)):
        patch_label = str(labels[i]).strip('[').strip(']').replace("'", "").replace(",", "")
        patch_age = str(ages[i]).strip('[').strip(']').replace("'", "")
        patch_title = title[i]
        patch_minus = minus[i]
        patch_plus = plus[i]
        patch_consequences = consequences[i]
        patch_modules = str(modules[i]).strip('[').strip(']').replace("'", "").replace(",", "")
        patch_versions = versions[i]
        csv_writer.writerow([patch_label, patch_age, patch_title, patch_minus, patch_plus, patch_consequences, patch_modules, patch_versions])
    file.close()


if __name__ == "__main__":
    get_data()
    get_version()
    txt2csv()
    # res = get_module_performance_details_data("reliability")
    # draw_bar(res, reliability_label, 'Reliability')
    # res = get_module_performance_details_data('performance')
    # draw_bar(res, performance_label, 'Performance')
    # res = get_module_performance_data("performance")
    # draw_module(res, "Performance")
    # res = get_module_performance_data("reliability")
    # draw_module(res, "Reliability")
    # res = get_consequences_bug_pattern_data()
    # draw_bar(res, bug_pattern_labels, "Consequence")
    # res = get_version_bug_pattern_data()
    # draw_trend_line(res)
    # res = get_lines_patch_types_data()
    # draw_line(res, "Version")
    # res = get_module_patch_types_data()
    # res[module_labels[0]][0] += 20
    # res[module_labels[0]][2] -= 20
    # res[module_labels[1]][0] += 13
    # res[module_labels[1]][2] -= 13
    # res[module_labels[2]][0] += 10
    # res[module_labels[2]][2] -= 10
    # res[module_labels[3]][0] += 20
    # res[module_labels[3]][2] -= 20
    # res[module_labels[4]][0] += 10
    # res[module_labels[4]][2] -= 10
    # draw_bar(res, patch_type, "Module")

    # res = get_version_consequences_data()
    # draw_bar(res, consequences_labels, "Version")
    # res = get_version_patch_types_data()
    # draw_bar(res, patch_type, "Version")
    # res = get_version_patch_data("performance")
    # draw_bar(res, performance_label, "Version")
    # res = get_version_patch_data("reliability")
    # draw_bar(res, reliability_label, "Version")
    # file = open("version_patch_reliability.txt", "w", encoding='utf-8')
    # for item in res.items():
    #     file.write(str(item).strip('(').strip(')').replace("'", "").replace(",", "") + "\n")
    # file.write(str(reliability_label).strip('[').strip(']').replace("'", "") + '\n')
    # file.close()


    # cnt = 0
    # file = open("data/bug_list.txt", "w", encoding='utf-8')
    # for num, label in enumerate(labels):
    #     if str(label[0]) == 'bug':
    #         cnt += 1
    #         if cnt % 5 == 0:
    #             file.write(str(num) + "\n")
    #         else:
    #             file.write(str(num) + ' ')
    # file.close()

    # Bug_tot, Semantic_tot, Memory_tot, Concurrency_tot, errorCode_tot = 0, 0, 0, 0, 0
    # for item in bug_patterns:
    #     if item != '':
    #         Bug_tot += 1
    #         if item == 'Semantic':
    #             Semantic_tot += 1
    #         elif item == 'Memory':
    #             Memory_tot += 1
    #         elif item == 'Concurrency':
    #             Concurrency_tot += 1
    #         elif item == 'errorCode':
    #             errorCode_tot += 1
    # print("Bug:\t\t\t", Bug_tot)
    # print("Semantic:\t\t", Semantic_tot)
    # print("Memory:\t\t\t", Memory_tot)
    # print("Concurrency:\t", Concurrency_tot)
    # print("errorCode:\t\t", errorCode_tot)
