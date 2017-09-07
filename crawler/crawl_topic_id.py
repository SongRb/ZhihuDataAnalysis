# coding=utf-8

from __future__ import unicode_literals, print_function

import cPickle as pickle
import collections
import os

from zhihu_oauth import ZhihuClient

TOKEN_FILE = 'token.pkl'

client = ZhihuClient()

if os.path.isfile(TOKEN_FILE):
    client.load_token(TOKEN_FILE)
else:
    client.login_in_terminal(use_getpass=False)
    client.save_token(TOKEN_FILE)

topic_queue = collections.deque()
topic_set = set()

topic_queue.append(19580349)
while len(topic_queue) > 0:
    root = topic_queue.popleft()
    print(root)
    topic = client.topic(root)
    topic_set.add(root)
    ans = topic.children
    for i in ans:
        for j in i.children:
            topic_queue.append(j.id)

print(len(topic_set))

with open('topic_set', b'w') as f:
    pickle.dump(topic_set, f)
