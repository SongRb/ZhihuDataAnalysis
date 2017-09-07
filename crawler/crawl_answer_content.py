import cPickle as pickle
import os
import time

import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from zhihu_oauth import ZhihuClient

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

ANSWER_DB2_FILE = 'answer_db2.pkl'
if os.path.isfile(ANSWER_DB2_FILE):
    with open(ANSWER_DB2_FILE, 'r') as f:
        answer_db2 = pickle.load(f)
else:
    answer_db2 = dict()

ANSWER_ID_LIST_FILE = 'answer_id_to_crawl.pkl'
with open(ANSWER_ID_LIST_FILE, 'r') as f:
    answer_id_list = pickle.load(f)

QUESTION_DB_FILE = 'question_db.pkl'
if os.path.isfile(QUESTION_DB_FILE):
    with open(QUESTION_DB_FILE, 'r') as f:
        question_db = pickle.load(f)
else:
    question_db = dict()

cnt = 100

TOKEN_FILE = 'token.pkl'
TOPIC_DB_FILE = 'topic_db.pkl'
ANSWER_DB_FILE = 'answer_db.pkl'

client = ZhihuClient()

if os.path.isfile(TOKEN_FILE):
    client.load_token(TOKEN_FILE)
else:
    client.login_in_terminal(use_getpass=False)
    client.save_token(TOKEN_FILE)

for ans_id in answer_id_list:
    if ans_id not in answer_db2:
        try:
            answer = client.answer(ans_id)
            print(cnt, answer.id)
            answer_db2[ans_id] = {
                'author': answer.author.id,
                'comment_count': answer.comment_count,
                'created_time': answer.created_time,
                'question': answer.question.id,
                'thanks_count': answer.thanks_count,
                'updated_time': answer.updated_time,
                'voteup_count': answer.voteup_count,
            }

            answer.save(path=os.path.join('data', 'answer'),
                        filename=os.path.join(str(answer.id)))
            cnt += 1

            if cnt % 100 == 0:
                with open(ANSWER_DB2_FILE, 'w') as f:
                    pickle.dump(answer_db2, f)

            if cnt % 200 == 0:
                print('Sleeping...')
                time.sleep(10)

            time.sleep(2)

        except:
            print("Error from server...")
            print("Saving Answer Database")
            with open(ANSWER_DB2_FILE, 'w') as f:
                pickle.dump(answer_db2, f)
                print(len(answer_db2))
            exit(0)
