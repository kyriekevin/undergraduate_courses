#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File    :   server.py    
@Contact :   2718629413@qq.com
@Software:   PyCharm

@Modify Time      @Author    @Version    @Description
------------      -------    --------    -----------
2022/3/29 20:40      zyz        1.0          None
"""
import socket

import matplotlib.pyplot as plt
import numpy as np

plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

if __name__ == "__main__":
    buf_size = 2048
    ip_port = ('127.0.0.1', 3943)
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server.bind(ip_port)
    cnt = 12

    temperature = []
    tempera = []

    while cnt:
        data, client_address = server.recvfrom(buf_size)
        print('server收到数据', data)
        server.sendto(data.upper(), client_address)
        cnt -= 1
        # temperature.append([12 - cnt, int(data)])
        # tempera.append(int(data))
        # tmp = np.array(temperature)
        # plt.scatter(tmp[:, 0], tmp[:, 1], c='coral', marker='*', s=200, alpha=0.5)
        # plt.plot(tmp[:, 0], tmp[:, 1], "aqua", ms=20)
        # plt.xlim(1, 12)
        # plt.ylim(19.5, 30.5)
        # plt.xlabel("时间")
        # plt.ylabel("温度")
        # plt.show()
        # plt.close()

    server.close()

    # labels = []
    # for i in range(len(tempera)):
    #     tmp = str(tempera[i]) + '℃'
    #     labels.append(tmp)
    # labels = np.array(labels)
    # labels = np.concatenate((labels, [labels[0]]))
    #
    # tempera = np.array(tempera)
    # tempera = np.concatenate((tempera, [tempera[0]]))
    # angles = np.linspace(0, 2 * np.pi, 12, endpoint=False)
    # angles = np.concatenate((angles, [angles[0]]))
    #
    # fig = plt.figure()
    # ax = fig.add_subplot(111, polar=True)
    # ax.plot(angles, tempera, 'ro-', linewidth=1)
    # ax.set_thetagrids(angles * 180 / np.pi, labels, fontproperties="SimHei")
    # ax.set_title("温度变化雷达图", va='bottom', fontproperties="SimHei")
    # ax.grid(True)
    # plt.show()
