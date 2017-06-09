# coding:utf-8

import whoosh.index as index
from whoosh.fields import *


def print_result(res):
    print 'Title:', res['title']
    print 'Content:', res['content']
    print


def print_all_res(results):
    length = len(results)
    if length > 10: length = 10
    if length == 0:
        print 'No result, try again'
    else:
        for i in range(length):
            print_result(results[i])


ix = index.open_dir("indexdir")
searcher = ix.searcher()

while True:
    query = raw_input("Please input your queries:").decode(sys.stdin.encoding)
    if query == 'quitt':
        break

    results = searcher.find('content', query)
    results2 = searcher.find('ques_title', query)

    print_all_res(results)
    print_all_res(results2)
