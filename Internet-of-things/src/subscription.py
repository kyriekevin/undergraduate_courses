#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File    :   subscription.py    
@Contact :   2718629413@qq.com
@Software:   PyCharm

@Modify Time      @Author    @Version    @Description
------------      -------    --------    -----------
2022/4/28 16:03      zyz        1.0          None
"""
import datetime
import json
import random
import re

import matplotlib.pyplot as plt
import requests
from paho.mqtt import client as mqtt_client

broker = '127.0.0.1'
port = 1883
topic = "temperature/#"
client_id = f'python-mqtt-{random.randint(0, 100)}'

# 存储三个服务器的数据
x1, y1 = [], []
x2, y2 = [], []
x3, y3 = [], []


# 画出对应的数据
def draw_all():
    if len(x1) > 11:
        plt.clf()
    plt.figure('all')
    plt.plot(x1, y1, c='r', ls='-', marker='o', mfc='w')  # 保存历史数据
    plt.plot(x2, y2, c='g', ls='-', marker='o', mfc='w')
    plt.plot(x3, y3, c='b', ls='-', marker='o', mfc='w')
    plt.xlabel("time")
    plt.ylabel("temperature")
    plt.savefig('all.jpg')


# 发送消息到dingding
def sent_msg_to_dingding(msg_id, temperature):
    url = 'https://oapi.dingtalk.com/robot/send?access_token=ca5112330a4622728c7fb6cf3757268d827489258cc855160aa2c7663edcea92'
    print(msg_id)
    msg = f'通知！{msg_id} 当前温度为 {temperature}'
    program = {
        "msgtype": "text",
        "text": {"content": msg}, }

    headers = {"Content-Type": "application/json ;charset=utf-8 "}
    requests.post(url, data=json.dumps(program), headers=headers)


# 对获取的数据进行处理
def deal_data(publish_id, temperature):
    if temperature >= 30:
        sent_msg_to_dingding(publish_id, temperature)

    if "mqtt0" in publish_id:
        x1.append(datetime.datetime.now())
        y1.append(temperature)
        if len(x1) > 10:
            x1.pop(0)
            y1.pop(0)
        plt.figure('mqtt1')
        plt.plot(x1, y1, c='r', ls='-', marker='o', mfc='w')  # 保存历史数据
        plt.xlabel("time")
        plt.ylabel("temperature")
        plt.savefig('mqtt1.jpg')

    if "mqtt1" in publish_id:
        x2.append(datetime.datetime.now())
        y2.append(temperature)
        if len(x2) > 10:
            x2.pop(0)
            y2.pop(0)
        plt.figure('mqtt2')
        plt.plot(x2, y2, c='g', ls='-', marker='o', mfc='w')
        plt.xlabel("time")
        plt.ylabel("temperature")
        plt.savefig('mqtt2.jpg')

    if "mqtt2" in publish_id:
        x3.append(datetime.datetime.now())
        y3.append(temperature)
        if len(x3) > 10:
            x3.pop(0)
            y3.pop(0)
        plt.figure('mqtt3')
        plt.plot(x3, y3, c='b', ls='-', marker='o', mfc='w')
        plt.xlabel("time")
        plt.ylabel("temperature")
        plt.savefig('mqtt3.jpg')
    draw_all()


# 连接到服务器
def connect_mqtt() -> mqtt_client:
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)

    client = mqtt_client.Client(client_id)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client


# 订阅主题和服务
def subscribe(client: mqtt_client):
    def on_message(client, userdata, msg):
        print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")
        s = re.split('{|}|\'|:', str(msg.payload))
        # deal_data(s[1], float(s[2]))

    client.subscribe(topic)
    client.on_message = on_message


def run():
    client = connect_mqtt()
    subscribe(client)
    client.loop_forever()


if __name__ == '__main__':
    run()
