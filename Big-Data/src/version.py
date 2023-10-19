#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File    :   version.py    
@Contact :   2718629413@qq.com
@Software:   PyCharm

@Modify Time      @Author    @Version    @Description
------------      -------    --------    -----------
2022/4/29 9:56      zyz        1.0          None
"""
import requests
from bs4 import BeautifulSoup


def get_version():
    url = "https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/refs/tags"
    web = "https://git.kernel.org"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36"
    }

    resp = requests.get(url, headers=headers)
    page = BeautifulSoup(resp.text, "html.parser")
    content = page.find("table", attrs={"class": "list nowrap"})
    trs = content.find_all("tr")[1:]

    f = open("data/version.txt", "w", encoding='utf-8')

    for tr in trs:
        tds = tr.find_all("td")
        version = tds[0].a.text
        link = tds[0].a.get('href')
        if '-' not in version and 'v2' not in version:
            web_link = web + link
            date_p = requests.get(web_link, headers=headers)
            date_page = BeautifulSoup(date_p.text, "html.parser")
            table = date_page.find("table", attrs={"class": "commit-info"})
            table_td = table.find_all('tr')[1].find_all('td')[1].text
            date = table_td.split()[0]
            f.write(version + "\t" + date + "\n")

    f.close()


if __name__ == "__main__":
    get_version()
