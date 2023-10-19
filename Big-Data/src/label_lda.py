#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File    :   label_lda.py
@Contact :   2718629413@qq.com
@Software:   PyCharm

@Modify Time      @Author    @Version    @Description
------------      -------    --------    -----------
2022/4/24 15:35      zyz        1.0          None
"""
import re
import string

import numpy as np
import requests
from bs4 import BeautifulSoup
from gensim import models, corpora
from nltk.corpus import stopwords
from nltk.stem.wordnet import WordNetLemmatizer


def get_data():
    web_url = "https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/log/ipc?showmsg=1&ofs="

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36"
    }

    ofs = ["0", "200", "400", "600", "800"]
    special_string = ["Link:", '[akpm@linux-foundation.org:', 'Cc:', 'Acked-by:', 'Signed-off-by:']
    doc = []

    for idx in ofs:
        url = web_url + idx

        resp = requests.get(url, headers=headers)
        page = BeautifulSoup(resp.text, "html.parser")
        content = page.find("div", attrs={"class": "content"})
        trs = content.find_all("tr")[1:]

        for tr in trs:
            if str(tr.get('class')[0]) == 'nohover-highlight':
                describe = tr.find_all("td")[1].text

                for item in special_string:
                    idx = describe.find(item)
                    if idx != -1:
                        describe = describe[:idx]

                doc.append(describe)

    return doc


def clean(doc):
    stop = set(stopwords.words('english'))
    punctuation = set(string.punctuation)
    lemma = WordNetLemmatizer()

    doc = ''.join([ch for ch in doc if not ch.isdigit()])
    doc = re.sub("@\S+", " ", doc)
    doc = re.sub("https*\S+", " ", doc)

    stop_free = ' '.join([ch for ch in doc.lower().split() if ch not in stop])
    punc_free = ''.join(ch for ch in stop_free if ch not in punctuation)
    normalized = ' '.join(lemma.lemmatize(word) for word in punc_free.split())
    return normalized


if __name__ == "__main__":
    origin_data = get_data()
    data_clean = [clean(doc).split() for doc in origin_data]
    dictionary = corpora.Dictionary(data_clean)
    corpus = [dictionary.doc2bow(doc) for doc in data_clean]
    Lda = models.ldamodel.LdaModel
    lda = Lda(corpus, num_topics=5, id2word=dictionary, passes=15)
    print(lda.print_topics(num_topics=5))

    labels = []
    doc_topic = lda.get_document_topics(corpus)
    index = np.arange(784, 874)
    for i in index:
        topic = np.array(doc_topic[i])
        topic_distribute = np.array(topic[:, 1])
        topic_idx = topic_distribute.argsort()[: -2: -1]
        labels.append(topic[topic_idx][0][0])
    labels = np.array(labels, dtype=np.int)
    file = open("data/labels.txt", "w", encoding='utf-8')
    file.write(str(labels).strip('[').strip(']').replace("'", ""))
    file.close()
