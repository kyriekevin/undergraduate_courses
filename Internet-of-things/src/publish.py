#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File    :   publish.py    
@Contact :   2718629413@qq.com
@Software:   PyCharm

@Modify Time      @Author    @Version    @Description
------------      -------    --------    -----------
2022/4/28 16:04      zyz        1.0          None
"""

import random
import time
from concurrent.futures import ThreadPoolExecutor

from paho.mqtt import client as mqtt_client

# 发送 温度temperature 主题消息
broker = '127.0.0.1'
port = 1883
topic = "temperature/"


# 随机生成温度
def data_generation():
    return format(random.uniform(10, 40), '.1f')


def connect_mqtt(client_id):
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)

    client = mqtt_client.Client(f'mqtt-{client_id}')
    client.on_connect = on_connect
    client.connect(broker, port)
    return client


def publish(client, client_id):
    count_success = 0
    count_error = 0
    msg_count = 0
    while msg_count < 20:
        time.sleep(random.randint(1, 3))
        cil_id = 'mqtt' + str(client_id)
        msg = f"{cil_id}:{data_generation()}"

        # 发送消息
        result = client.publish(topic, msg)
        status = result[0]

        if status == 0:
            print(f"Send `{msg}` to topic `{topic}`")
            count_success += 1
        else:
            print(f"Failed to send '{msg}' to topic {topic}")
            count_error += 1
        msg_count += 1

    print(f"发送成功{count_success}")
    print(f"发送失败{count_error}")


def run(client_id):
    # 传感器
    client1 = connect_mqtt(client_id)
    client1.loop_start()
    publish(client1, client_id)


if __name__ == '__main__':
    pool = ThreadPoolExecutor(3)
    for i in range(3):
        pool.submit(run, i)
