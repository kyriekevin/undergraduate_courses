#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File    :   模拟退火.py    
@Contact :   2718629413@qq.com
@Software:   PyCharm

@Modify Time      @Author    @Version    @Description
------------      -------    --------    -----------
2022/3/4 19:15      zyz        1.0          None
"""
import math
import random

import matplotlib.pyplot as plt
import numpy as np


class City:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __repr__(self):
        return "(" + str(self.x) + "," + str(self.y) + ")"


def get_distance(ca, cb):
    """
    计算城市欧式距离
    :param ca: 城市A
    :param cb: 城市B
    :return: 两城市距离
    """
    dx = ca.x - cb.x
    dy = ca.y - cb.y
    dist = np.sqrt(dx * dx + dy * dy)
    return dist


def distance_cities():
    """
    计算城市间距离
    :return: 城市间距离
    """
    dist_list = {}
    for i in range(len(city_list)):
        for j in range(len(city_list)):
            if i > j:
                dist = get_distance(city_list[i], city_list[j])
                dist_list[(i, j)] = dist
                dist_list[(j, i)] = dist

    return dist_list


def cal_fit(x):
    """
    计算适应度
    :param x: 序列
    :return: 总距离
    """
    tot_dist = distance_list[(x[-1], x[0])]
    for i in range(num_city - 1):
        tot_dist += distance_list[(x[i], x[i + 1])]
    return tot_dist


def init_parameter():
    """
    初始化模拟退火参数
    :return: 模拟退火所需参数
    """
    t0 = 1e7
    t1 = 1e-7
    original_alpha = 0.98
    original_markov = 1000
    original_pm = 0.3
    original_pc = 0.7
    return t0, t1, original_alpha, original_markov, original_pm, original_pc


def simulate_anneal():
    """
    模拟退火算法
    :return: 最佳路径和对应距离
    """
    t_init, t_final, alpha, markov_len, pm, pc = init_parameter()

    best_route = None
    best_fit = math.inf
    x = np.zeros([markov_len, num_city])
    fit = np.zeros([markov_len])

    for i in range(markov_len):
        x[i] = np.random.permutation(num_city)
        fit[i] = cal_fit(x[i])
        if fit[i] < best_fit:
            best_fit = fit[i]
            best_route = x[i].copy()

    t = t_init
    while t >= t_final:
        for i in range(markov_len):
            cur = x[i].copy()
            if random.random() < pm:
                point1 = int(random.random() * num_city)
                point2 = int(random.random() * num_city)
                while point1 == point2:
                    point1 = int(random.random() * num_city)
                    point2 = int(random.random() * num_city)
                cur[point1], cur[point2] = cur[point2], cur[point1]

            if random.random() < pc:
                point = int(random.random() * num_city)
                temp1 = list(cur[0: point])
                temp2 = list(cur[point: num_city])
                temp2.extend(temp1)
                cur = np.array(temp2.copy())

            cur_fit = cal_fit(cur)
            delta = cur_fit - fit[i]
            if delta <= 0:
                fit[i] = cur_fit
                x[i] = cur
                if fit[i] < best_fit:
                    best_fit = fit[i]
                    best_route = x[i].copy()
            elif random.random() < math.exp(-delta / t):
                fit[i] = cur_fit
                x[i] = cur.copy()

        best_data.append(best_fit)
        t *= alpha

    return best_route, best_fit


def draw(route, fit):
    """
    绘制
    :param route: 路径
    :param fit: 距离
    :return:
    """
    path = list(route)
    path.append(path[0])
    city_x, city_y = [], []

    for idx in path:
        idx = int(idx)
        city_x.append(city_list[idx].x)
        city_y.append(city_list[idx].y)

    plt.scatter(city_x, city_y, c='r', marker='*', s=200, alpha=0.5)
    plt.plot(city_x, city_y, "b", ms=20)
    plt.title('Simulated Annealing Algorithm\n' + 'tot_dist = ' + str(round(fit, 3)))
    plt.savefig('sa_route.jpg')
    plt.show()

    plt.plot(range(len(best_data)), best_data)
    plt.title('Iteration_BestFit')
    plt.xlabel('iteration')
    plt.ylabel('distance')
    plt.savefig('sa_iteration.jpg')
    plt.show()


if __name__ == "__main__":
    city_list = []
    best_data = []
    num_city = 34

    with open('city.txt', 'r', encoding='UTF-8') as f:
        lines = f.readlines()

    for line in lines:
        line = line.replace('\n', '')
        city = line.split('\t')
        city_list.append(City(float(city[1]), float(city[2])))

    distance_list = distance_cities()
    best_path, best_fitness = simulate_anneal()
    draw(best_path, best_fitness)
