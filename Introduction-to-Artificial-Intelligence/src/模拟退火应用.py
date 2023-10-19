#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File    :   模拟退火应用.py    
@Contact :   2718629413@qq.com
@Software:   PyCharm

@Modify Time      @Author    @Version    @Description
------------      -------    --------    -----------
2022/4/14 20:48      zyz        1.0          None
"""

import math
import random

import matplotlib.pyplot as plt

"""
目标函数
f(x)=11*sin(6*x)+7*cos(5*x),x∈[0,2*pi]
"""

# 设置随机种子, 用于调参
random.seed(39)
PI2 = math.pi * 2


def f(x):
    """
    定义目标函数
    :param x: 自变量x
    :return: 目标函数
    """

    return 11 * math.sin(6 * x) + 7 * math.cos(5 * x)


def init_parameter():
    """
    初始化参数
    """

    t_init = 1e2
    alpha = 0.998
    k = 0.5
    markov = 150
    index = 0
    t_final = 1e-2
    return t_init, alpha, k, markov, index, t_final


def draw_path(fits):
    """
    退火的结果
    """

    plt.plot(range(len(fits)), fits)
    plt.title('Iteration_BestFit: ' + str(min(fits)))
    plt.xlabel('iteration')
    plt.ylabel('best result')
    plt.savefig('sa_func_iteration.jpg')
    plt.show()


def sa():
    """
    模拟退火
    """

    location = []
    e_collection = []
    t, alpha, k, markov, index, t_final = init_parameter()
    # 最优解
    best_e = f(index)
    c = 0
    location.append([0, best_e])
    e_collection.append(best_e)
    while t > t_final:
        markov_t = markov
        o_e = best_e
        o_index = index
        while markov_t > 0:
            i_index = random.uniform(index, min(index + k, PI2))
            i_e = f(i_index)
            # 下一步的能量f(i_index)<f(o_index)
            if i_e < o_e:
                o_e = i_e
                o_index = i_index
            else:
                p = math.e ** ((i_e - o_e) / t)
                if random.uniform(0, p) < p:
                    o_e = i_e
                    o_index = i_index
            location.append([i_index, i_e])
            markov_t -= 1

        if o_e < best_e:
            best_e = o_e
            index = o_index
            c = 0
        else:
            c += 1
        if c >= 5:
            break
        e_collection.append(best_e)
        t *= alpha
    draw_path(e_collection)
    return best_e


if __name__ == "__main__":
    print(sa())
