#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File    :   client.py    
@Contact :   2718629413@qq.com
@Software:   PyCharm

@Modify Time      @Author    @Version    @Description
------------      -------    --------    -----------
2022/3/29 20:44      zyz        1.0          None
"""
import random
import socket
import time


def data_generation():
    temperature = random.randint(20, 30)
    return str(temperature)


if __name__ == "__main__":
    buf_size = 2048
    ip_port = ('127.0.0.1', 3943)
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    cnt = 12

    while cnt:
        msg = data_generation()
        client.sendto(msg.encode('utf-8'), ip_port)
        data, server_address = client.recvfrom(buf_size)
        print('客户端 receive from', data, server_address)
        time.sleep(1)
        cnt -= 1

    client.close()
