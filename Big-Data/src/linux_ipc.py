#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File    :   linux_ipc.py    
@Contact :   2718629413@qq.com
@Software:   PyCharm

@Modify Time      @Author    @Version    @Description
------------      -------    --------    -----------
2022/4/22 13:14      zyz        1.0          None
"""
import requests
from bs4 import BeautifulSoup
import csv


def get_data():
    web_url = "https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/log/ipc?showmsg=1&ofs="

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36"
    }

    index = ["0", "200", "400", "600", "800"]
    f = open("data/data.csv", mode="w", encoding='utf-8')
    csvwriter = csv.writer(f)
    cnt = 0

    for idx in index:
        url = web_url + idx

        resp = requests.get(url, headers=headers)
        page = BeautifulSoup(resp.text, "html.parser")
        content = page.find("div", attrs={"class": "content"})
        trs = content.find_all("tr")[1:]

        age, title, link, lines, category_file = "", "", "", "", ""
        for tr in trs:
            if str(tr.get('class')[0]) == 'logheader':
                tds = tr.find_all("td")
                age = tds[0].text
                title = tds[1].text
                link = "https://git.kernel.org" + tds[1].a.get('href')
                category_cnt = tds[3].text
                lines = tds[4].text
                category_p = requests.get(link, headers=headers)
                category_page = BeautifulSoup(category_p.text, "html.parser")
                if int(category_cnt) == 1:
                    category_content = category_page.find('td', attrs={'class': 'upd'})
                    category_file = category_content.text
                else:
                    category_file = ""
                    category_content = category_page.find('table', attrs={'class': 'diffstat'})
                    category_trs = category_content.find_all("tr")[:]
                    for category_tr in category_trs:
                        category_tds = category_tr.find_all("td")
                        if str(category_tds[1].get('class')[0]) == 'upd':
                            category_file += str(category_tds[1].a.text) + " "
            elif str(tr.get('class')[0]) == 'nohover-highlight':
                describe = tr.find_all("td")[1].text
                csvwriter.writerow([age, title, link, lines, describe, category_file])
                file = open("data/" + str(cnt) + '.txt', "w", encoding='utf-8')
                file.write("age: " + age + '\n')
                file.write("title: " + title + '\n')
                file.write("link: " + link + '\n')
                file.write("lines: " + lines + '\n')
                file.write("category: " + category_file + '\n')
                file.write(describe)
                file.close()
                cnt += 1

    f.close()


if __name__ == "__main__":
    get_data()
