#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File    :   mqtt.py    
@Contact :   2718629413@qq.com
@Software:   PyCharm

@Modify Time      @Author    @Version    @Description
------------      -------    --------    -----------
2022/5/13 14:44      zyz        1.0          None
"""
import json

import paho.mqtt.client as mqtt
import random
import time
import datetime
import csv

original_data = [3, 80, 25, 4, 70]
access = 'czXZHUPqTsZgbHdV2s1B'
broker = 'demo.thingsboard.io'
port = 1883

log_path = 'log.csv'
file = open(log_path, 'a+', encoding='utf-8', newline='')
csv_writer = csv.writer(file)
# csv_writer.writerow([f'紫外线强度', '空气污染指数', '温度', '风力', '湿度'])

def on_publish(client, userdata, result):
    pass
    # print("sending...")


def on_connect(client, userdata, flag, rc):
    pass
    # print(str(rc))
    # print("connected")


def generate_data(t):
    temp = {}
    global original_data
    if t != 0:
        if t % 5 == 0:
            original_data[2] = min(37, max(original_data[2] + random.randint(-2, 2), 15))
            original_data[3] = max(1, min(9, original_data[3] + random.randint(-1, 1)))
        if t % 10 == 0:
            original_data[0] = max(1, min(9, original_data[0] + random.randint(-1, 1)))
            original_data[4] = max(50, min(90, original_data[4] + random.randint(-3, 3)))
        if t % 15 == 0:
            original_data[1] = max(1, min(200, original_data[1] + random.randint(-5, 5)))

    temp['紫外线强度'] = original_data[0]
    temp['空气污染指数'] = original_data[1]
    temp['温度'] = original_data[2]
    temp['风力'] = original_data[3]
    temp['湿度'] = original_data[4]
    temp['24小时'] = original_data[2]
    csv_writer.writerow([temp['紫外线强度'], temp['空气污染指数'], temp['温度'], temp['风力'], temp['湿度']])

    return temp


test = mqtt.Client("device1")
test.on_publish = on_publish
test.on_connect = on_connect
test.username_pw_set(access)
test.connect(broker, port, keepalive=60)con
test.loop_start()

start = time.time()
cur = start
while True:
    data = generate_data(int(cur - start))
    print(data)
    test.publish('v1/devices/me/telemetry', payload=json.dumps(data), qos=0)
    time.sleep(3)
    cur = time.time()
    if cur - start >= 30:
        file.close()
        break

