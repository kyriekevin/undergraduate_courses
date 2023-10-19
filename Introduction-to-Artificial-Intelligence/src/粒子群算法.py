#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File    :   粒子群算法.py    
@Contact :   2718629413@qq.com
@Software:   PyCharm

@Modify Time      @Author    @Version    @Description
------------      -------    --------    -----------
2022/4/1 21:07      zyz        1.0          None
"""

import random
import numpy as np

import matplotlib.pyplot as plt
from matplotlib.pylab import mpl
from scipy import spatial

mpl.rcParams['font.sans-serif'] = ['SimHei']


def cal_fitness(path, dis_mat):
    """
    计算路径距离，即评价函数
    :param path 路径
    :param dis_mat 城市间距离矩阵
    :return 路径距离
    """
    dis_sum = 0
    for i in range(len(path) - 1):
        dis = dis_mat[path[i], path[i + 1]]
        dis_sum = dis_sum + dis
    dis = dis_mat[path[-1], path[0]]
    dis_sum = dis_sum + dis
    return round(dis_sum, 1)


def draw_path(path, city_list, g_best, fit):
    """
    路径图
    :param path 路径
    :param city_list 城市坐标
    :param g_best 全局最优解
    :param fit
    :return 路径图
    """
    x, y = [], []
    for i in path:
        coordinate = city_list[i]
        x.append(coordinate[0])
        y.append(coordinate[1])
    x.append(x[0])
    y.append(y[0])
    plt.scatter(x, y, c='r', marker='*', s=200, alpha=0.5)
    plt.plot(x, y, "b", ms=20)
    plt.title('pso\n' + 'tot_dist = ' + str(g_best))
    plt.savefig('pso_route.jpg')
    plt.show()

    plt.plot(range(len(fit)), fit)
    plt.title('Iteration_BestFit')
    plt.xlabel('iteration')
    plt.ylabel('distance')
    plt.savefig('pso_iteration.jpg')
    plt.show()


def crossover(bird, pline, g_line, w, c1, c2):
    """
    :param bird 粒子
    :param pline 当前最优解
    :param g_line 全局最优解
    :param w 惯性因子
    :param c1 自我认知因子
    :param c2 社会认知因子
    :return 交叉后的粒子
    """
    cro_bird = [None] * len(bird)
    parent1 = bird

    rand_num = random.uniform(0, sum([w, c1, c2]))
    if rand_num <= w:
        parent2 = [bird[i] for i in range(len(bird) - 1, -1, -1)]
    elif rand_num <= w + c1:
        parent2 = pline
    else:
        parent2 = g_line

    # parent1-> croBird
    start_pos = random.randint(0, len(parent1) - 1)
    end_pos = random.randint(0, len(parent1) - 1)
    if start_pos > end_pos:
        start_pos, end_pos = end_pos, start_pos
    cro_bird[start_pos:end_pos + 1] = parent1[start_pos:end_pos + 1].copy()

    # parent2 -> croBird
    list1 = list(range(0, start_pos))
    list2 = list(range(end_pos + 1, len(parent2)))
    list_index = list1 + list2  # croBird从后往前填充
    j = -1
    for i in list_index:
        for j in range(j + 1, len(parent2) + 1):
            if parent2[j] not in cro_bird:
                cro_bird[i] = parent2[j]
                break

    return cro_bird


if __name__ == '__main__':
    # PSO参数
    tot_iter = 800  # 迭代次数
    iter_num = 1  # 当前迭代次数
    birdNum = 100  # 粒子数量
    w = 0.2  # 惯性因子
    c1 = 0.4  # 自我认知因子
    c2 = 0.4  # 社会认知因子
    pBest, pLine = 0, []  # 当前最优值、当前最优解，（自我认知部分）
    gBest, gLine = 0, []  # 全局最优值、全局最优解，（社会认知部分）

    cityList = []
    with open('city.txt', 'r', encoding='utf-8') as f:
        lines = f.readlines()

    for line in lines:
        line = line.replace('\n', '')
        city = line.split('\t')
        cityList.append([float(city[1]), float(city[2])])

    cityList = np.array(cityList)
    dis_matrix = spatial.distance.cdist(cityList, cityList, metric='euclidean')

    birdPop = [random.sample(range(len(cityList)), len(cityList)) for i in range(birdNum)]  # 初始化种群，随机生成

    fits = [cal_fitness(birdPop[i], dis_matrix) for i in range(birdNum)]  # 计算种群适应度
    gBest = pBest = min(fits)  # 全局最优值、当前最优值
    gLine = pLine = birdPop[fits.index(min(fits))]  # 全局最优解、当前最优解

    globals_fits = [gBest]
    while iter_num <= tot_iter:  # 迭代开始
        for i in range(len(birdPop)):
            birdPop[i] = crossover(birdPop[i], pLine, gLine, w, c1, c2)
            fits[i] = cal_fitness(birdPop[i], dis_matrix)

        pBest, pLine = min(fits), birdPop[fits.index(min(fits))]
        if pBest <= gBest:
            gBest, gLine = pBest, pLine
        globals_fits.append(gBest)

        iter_num += 1
    print(gLine)
    draw_path(gLine, cityList, gBest, globals_fits)
