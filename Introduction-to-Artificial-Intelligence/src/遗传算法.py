#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File    :   遗传算法.py    
@Contact :   2718629413@qq.com
@Software:   PyCharm

@Modify Time      @Author    @Version    @Description
------------      -------    --------    -----------
2022/3/4 16:20      zyz        1.0          None
"""
import copy
import random

import matplotlib.pyplot as plt
import numpy as np


class City:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __repr__(self):
        return "(" + str(self.x) + "," + str(self.y) + ")"

    def __getitem__(self, item):
        return self.__dict__[item]


def distance(ca, cb):
    """
    计算城市欧式距离
    :param ca: 城市A
    :param cb: 城市B
    :return: 两城市距离
    """
    dx = ca.x - cb.x
    dy = ca.y - cb.y
    d = np.sqrt(dx * dx + dy * dy)
    return d


def init_pop(population_size):
    """
    初始化种群
    :param population_size: 种群规模
    :return: 初始化后的种群
    """
    pop = []
    for i in range(population_size):
        new_city_list = random.sample(city_list, len(city_list))
        pop.append(new_city_list)

    return pop


def fitness(population):
    """
    计算适应度
    :param population: 种群
    :return: 种群适应度
    """
    dis_cities = distance_cities(population)
    return 1.0 / dis_cities


def distance_cities(population):
    """
    计算城市间距离
    :param population: 种群
    :return: 城市间距离总和
    """
    temp_distance = 0
    for i in range(len(population) - 1):
        temp_distance += distance(population[i], population[i + 1])
    temp_distance += distance(population[len(population) - 1], population[0])

    return temp_distance


def rank(population):
    """
    适应度排序
    :param population: 种群
    :return: 适应度排序
    """
    rank_pop_dic = {}
    for i in range(len(population)):
        fit = fitness(population[i])
        rank_pop_dic[i] = fit

    return sorted(rank_pop_dic.items(), key=lambda x: x[1], reverse=True)


def select(population, population_rank, elite_size):
    """
    精英选择策略加上轮盘赌选择
    :param population: 种群
    :param population_rank: 种群排名
    :param elite_size: 精英个数
    :return: 选择出的种群
    """
    select_pop = []
    for i in range(elite_size):
        select_pop.append(population[population_rank[i][0]])

    cumsum = 0
    cumsum_list = []
    temp_pop = copy.deepcopy(population_rank)
    for i in range(len(temp_pop)):
        cumsum += temp_pop[i][1]
        cumsum_list.append(cumsum)
    for i in range(len(temp_pop)):
        cumsum_list[i] /= cumsum

    for i in range(len(temp_pop) - elite_size):
        r = random.random()
        for j in range(len(temp_pop)):
            if cumsum_list[j] > r:
                select_pop.append(population[population_rank[i][0]])
                break

    return select_pop


def breed(population, elite_size):
    """
    种群繁殖
    :param population: 种群
    :param elite_size: 精英个数
    :return: 繁殖后的种群
    """
    breed_population = []
    for i in range(elite_size):
        breed_population.append(population[i])

    i = 0
    while i < (len(population) - elite_size):
        a = random.randint(0, len(population) - 1)
        b = random.randint(0, len(population) - 1)
        if a != b:
            fa, fb = population[a], population[b]
            gene_a, gene_b = random.randint(0, len(population[a]) - 1), random.randint(0, len(population[b]) - 1)
            start_gene = min(gene_a, gene_b)
            end_gene = max(gene_a, gene_b)
            child1 = []
            for j in range(start_gene, end_gene):
                child1.append(fa[j])
            child2 = []
            for j in fb:
                if j not in child1:
                    child2.append(j)
            breed_population.append(child1 + child2)
            i = i + 1

    return breed_population


def mutate(population, mutation_rate):
    """
    种群变异
    :param population: 种群
    :param mutation_rate: 变异率
    :return: 变异后的种群
    """
    mutation_population = []
    for i in range(len(population)):
        for j in range(len(population[i])):
            r = random.random()
            if r < mutation_rate:
                a = random.randint(0, len(population[i]) - 1)
                population[i][a], population[i][j] = population[i][j], population[i][a]
        mutation_population.append(population[i])

    return mutation_population


def next_pop(population, elite_size, mutation_rate):
    """
    产生下一代
    :param population: 种群
    :param elite_size: 精英个数
    :param mutation_rate: 变异率
    :return: 产生出的下一代
    """
    pop_rank = rank(population)  # 按照适应度排序
    select_pop = select(population, pop_rank, elite_size)  # 精英选择策略，加上轮盘赌选择
    breed_pop = breed(select_pop, elite_size)  # 繁殖
    next_generation = mutate(breed_pop, mutation_rate)  # 变异

    return next_generation


def get_path(best_route):
    """
    获得路径
    :param best_route: 最佳路径
    :return: 路径
    """
    x = []
    y = []
    for j in range(len(best_route)):
        c = best_route[j]
        x.append(c.x)
        y.append(c.y)
    x.append(best_route[0].x)
    y.append(best_route[0].y)
    return x, y


def ga(population_size, elite_size, mutation_rate, generations, dynamic):
    """
    遗传算法
    :param population_size: 种群规模
    :param elite_size: 精英规模
    :param mutation_rate: 变异率
    :param generations: 这一代
    :param dynamic: 是否动态画图
    :return: 过程,城市x坐标,城市y坐标,最佳路线距离
    """
    population = init_pop(population_size)  # 初始化种群

    if dynamic:
        plt.figure('Map')
        plt.ion()

    print("initial distance:{}".format(1.0 / (rank(population)[0][1])))
    for i in range(generations):
        population = next_pop(population, elite_size, mutation_rate)  # 产生下一代种群
        process.append(1.0 / (rank(population)[0][1]))
        if dynamic:
            plt.cla()
            idx_rank_pop = rank(population)[0][0]
            best_route = population[idx_rank_pop]
            c_x, c_y = get_path(best_route)
            plt.scatter(c_x, c_y, c='r', marker='*', s=200, alpha=0.5)
            plt.plot(c_x, c_y, "b", ms=20)
            plt.pause(0.3)

    print("final distance:{}".format(1.0 / (rank(population)[0][1])))
    best_dist = 1.0 / rank(population)[0][1]
    best_route_index = rank(population)[0][0]
    best_result = population[best_route_index]
    if dynamic:
        plt.ioff()
        plt.show()
        return best_result
    else:
        c_x, c_y = get_path(best_result)
        return c_x, c_y, best_dist


def draw(note):
    """
    绘制
    :param note: 标记
    :return:
    """
    for i in range(len(res)):
        p = res[i]
        plt.subplot(2, 3, i + 1)
        plt.plot(p)
        plt.ylabel('Distance')
        plt.xlabel('Generation')
    plt.suptitle('test_' + note + '_process')
    plt.tight_layout()
    plt.savefig('ga_process_' + note + '.jpg')
    plt.show()

    for i in range(len(City_x)):
        path_x = City_x[i]
        path_y = City_y[i]
        plt.subplot(2, 3, i + 1)
        plt.scatter(path_x, path_y, c='r', marker='*', s=200, alpha=0.5)
        plt.plot(path_x, path_y, "b", ms=20)
    plt.suptitle('test_' + note + '_route')
    plt.tight_layout()
    plt.savefig('ga_route_' + note + '.jpg')
    plt.show()


def init_parameter():
    """
    初始化遗传算法所需参数
    :return: 返回初始化参数
    """
    original_route = 1e9
    original_epoch = 2500
    original_rate = 0.01
    original_population_size = 100
    original_elite_size = 20

    return original_route, original_epoch, original_rate, original_population_size, original_elite_size


def test(string):
    global best_rate, best_epoch, best_path
    if string == "epoch":
        arr = epoch
    else:
        arr = rate
    for item in arr:
        if string == "epoch":
            city_x, city_y, dist = ga(population_num, elite_num, best_rate, item, dynamic=False)
        else:
            city_x, city_y, dist = ga(population_num, elite_num, item, best_epoch, dynamic=False)
        if dist < best_path:
            best_path = dist
            if string == "epoch":
                best_epoch = item
            else:
                best_rate = item
        res.append(process.copy())
        process.clear()
        City_x.append(city_x)
        City_y.append(city_y)
    draw(string)


if __name__ == "__main__":
    num_city = 34
    city_list, res = [], []
    City_x, City_y = [], []
    process = []
    epoch = [50, 100, 500, 1000, 2500, 5000]
    rate = [0.001, 0.005, 0.01, 0.05, 0.1, 0.2]

    with open('city.txt', 'r', encoding='UTF-8') as f:
        lines = f.readlines()

    for line in lines:
        line = line.replace('\n', '')
        city = line.split('\t')
        city_list.append(City(float(city[1]), float(city[2])))

    best_path, best_epoch, best_rate, population_num, elite_num = init_parameter()
    test("epoch")
    res.clear()
    City_x.clear()
    City_y.clear()
    test("rate")
    ga(100, 20, best_rate, best_epoch, dynamic=True)

