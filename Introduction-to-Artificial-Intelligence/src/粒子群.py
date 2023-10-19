#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File    :   粒子群.py    
@Contact :   2718629413@qq.com
@Software:   PyCharm

@Modify Time      @Author    @Version    @Description
------------      -------    --------    -----------
2022/3/4 21:23      zyz        1.0          None
"""
import matplotlib.pyplot as plt
import numpy as np
from scipy import spatial
from sko.PSO import PSO_TSP


def init_parameter():
    """
    初始化粒子群参数
    :return: 粒子群算法所需参数
    """
    original_epoch = 1000
    original_w = 0.8
    original_c1 = 0.1
    original_c2 = 0.1
    return original_epoch, original_w, original_c1, original_c2


def cal_total_distance(routine):
    """
    计算总路径
    :param routine: 路径
    :return: 总路径
    """
    num_points, = routine.shape
    return sum([distance_matrix[routine[i % num_points], routine[(i + 1) % num_points]] for i in range(num_points)])


def draw():
    """
    绘制
    :return:
    """
    fig, ax = plt.subplots(1, 2)
    best_points_ = np.concatenate([best_points, [best_points[0]]])
    best_points_coordinate = city_list[best_points_, :]
    ax[0].scatter(best_points_coordinate[:, 0], best_points_coordinate[:, 1], c='r', marker='*', s=200, alpha=0.5)
    ax[0].plot(best_points_coordinate[:, 0], best_points_coordinate[:, 1], "b", ms=20)
    ax[1].plot(pso_tsp.gbest_y_hist)
    plt.ylabel('Distance')
    plt.xlabel('Generation')
    plt.suptitle('pso_tsp')
    plt.tight_layout()
    plt.savefig('pso.jpg')
    plt.show()


if __name__ == "__main__":
    num_city = 34
    city_list = []

    with open('city.txt', 'r', encoding='UTF-8') as f:
        lines = f.readlines()

    for line in lines:
        line = line.replace('\n', '')
        city = line.split('\t')
        city_list.append([float(city[1]), float(city[2])])

    city_list = np.array(city_list)
    # 获得距离矩阵
    distance_matrix = spatial.distance.cdist(city_list, city_list, metric='euclidean')

    best_epoch, best_w, best_c1, best_c2 = init_parameter()

    pso_tsp = PSO_TSP(func=cal_total_distance, n_dim=num_city, size_pop=200, max_iter=best_epoch, w=best_w, c1=best_c1,
                      c2=best_c2)
    best_points, best_distance = pso_tsp.run()
    draw()
