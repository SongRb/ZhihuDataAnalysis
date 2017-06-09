# coding:utf-8
import json
import os

import jieba
from whoosh.analysis import Tokenizer, Token
from whoosh.fields import *
from whoosh.index import create_in


class ChineseTokenizer(Tokenizer):
    def __call__(self, value, positions=False, chars=False,
                 keeporiginal=False, removestops=True,
                 start_pos=0, start_char=0, mode='', **kwargs):
        # assert isinstance(value, text_type), "%r is not unicode" % value
        t = Token(positions, chars, removestops=removestops, mode=mode,
                  **kwargs)
        seglist = jieba.cut_for_search(value)  # 使用结巴分词库进行分词
        for w in seglist:
            t.original = t.text = w
            t.boost = 1.0
            if positions:
                t.pos = start_pos + value.find(w)
            if chars:
                t.startchar = start_char + value.find(w)
                t.endchar = start_char + value.find(w) + len(w)
            yield t  # 通过生成器返回每个分词的结果token


def ChineseAnalyzer():
    return ChineseTokenizer()


analyzer = ChineseAnalyzer()


def index():
    schema = Schema(title=TEXT(stored=True), path=ID(stored=True),
                    content=TEXT(stored=True, analyzer=analyzer),
                    ques_title=TEXT(stored=True, analyzer=analyzer)

                    )

    if not os.path.exists('indexdir'):
        os.makedirs('indexdir')

    ix = create_in('indexdir', schema)

    ans_db = dict()

    if os.path.exists('answer'):
        with open('answer', 'r') as f:
            ans_db = json.load(f)

    writer = ix.writer()
    for id in ans_db:
        writer.add_document(title=ans_db[id]['question']['title'], path=u'/a',
                            content=ans_db[id]['excerpt'],
                            ques_title=ans_db[id]['question']['title']
                            )
    writer.commit()


if __name__ == '__main__':
    index()
