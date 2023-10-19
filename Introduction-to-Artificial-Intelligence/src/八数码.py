#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File    :   八数码.py    
@Contact :   2718629413@qq.com
@Software:   PyCharm

@Modify Time      @Author    @Version    @Description
------------      -------    --------    -----------
2022/3/5 10:33      zyz        1.0           None
"""
import heapq  # 定义优先队列


# 估价函数
def f(s):
    """
    :param s: 状态
    :return: 哈曼顿距离 （数当前的坐标和理想位置坐标差的绝对值和）
    """
    res = 0
    for idx in range(9):
        if s[idx] != 'x':
            pos = int(s[idx]) - 1
            res += abs(idx // 3 - pos // 3) + abs(idx % 3 - pos % 3)
    return res


# 交换字符串中的指定字符
def swap(i, j):
    global start
    """
    :param idx1: 要交换字符的位置下标
    :param idx2: 要交换字符的位置下标
    :return: 目标字符串
    """
    tmp = start[j]
    trailer = start[j + 1:] if j + 1 < len(start) else ''
    start = start[0: j] + start[i] + trailer
    start = start[0: i] + tmp + start[i + 1:]
    return start


# 将字符串以八数码格式输出
def output():
    """
    :return:
    """
    for i in range(3):
        for j in range(3):
            print(start[3 * i + j], end=" ")
        print("")
    print("")


# 宽度优先搜索 + A* + 优先队列
def bfs():
    global start
    """
    :return:
    """
    op = 'udlr'
    direction = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    end = '12345678x'
    # 优先级队列
    q = [(f(start), start)]
    # 状态转移的哈希表
    pre = {}
    # 距离哈希表
    d = {}
    d[start] = 0
    while q:
        cur = heapq.heappop(q)[1]
        if cur == end:
            break
        # 找到'x'的索引
        j = cur.find('x')
        # 求坐标
        x, y = j // 3, j % 3
        # 备份现场
        init = cur
        # 枚举变化
        for i in range(4):
            nx = x + direction[i][0]
            ny = y + direction[i][1]
            if nx < 0 or nx >= 3 or ny < 0 or ny >= 3:
                continue
            cur = list(cur)
            cur[j], cur[3 * nx + ny] = cur[3 * nx + ny], cur[j]
            cur = ''.join(cur)
            if cur not in d or d[cur] > d[init] + 1:
                d[cur] = d[init] + 1
                pre[cur] = (init, op[i])
                heapq.heappush(q, (d[cur] + f(cur), cur))
            cur = init

    ans = ''
    while end != start:
        ans += pre[end][1]
        end = pre[end][0]

    # 这里是从结尾到起点的，所以应该翻转
    ans = ans[::-1]
    print(ans)
    print(start, f(start))
    output()

    # 输出中间过程
    pos = start.find('x')
    for ch in ans:
        if ch == 'u':
            start = swap(pos - 3, pos)
            pos -= 3
        elif ch == 'd':
            start = swap(pos, pos + 3)
            pos += 3
        elif ch == 'r':
            start = swap(pos, pos + 1)
            pos += 1
        else:
            start = swap(pos - 1, pos)
            pos -= 1

        print(ch, start, f(start))
        output()


if __name__ == "__main__":
    start = input().replace(' ', '').strip()
    start_t = start.replace('x', '')
    temp = 0

    # 求逆序对个数
    for k in range(len(start_t)):
        for t in range(k, len(start_t)):
            if start_t[t] < start_t[k]:
                temp += 1

    if temp & 1:
        print('unsolvable')
    else:
        bfs()
