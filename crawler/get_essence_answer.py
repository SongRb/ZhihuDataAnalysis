# Python 2.x
import cPickle as pickle
import os
import time

import requests
from zhihu_oauth import *


def get_dict_database(filename):
    if os.path.isfile(filename):
        with open(filename, 'r') as f:
            return pickle.load(f)
    else:
        return dict()


def get_essence_answer():
    max_count = 0
    for topic_id in obj:
        if topic_id not in topic_db:
            print(topic_id)
            topic_db[topic_id] = dict()

            try:
                topic_data = client.topic(topic_id)
                topic_db[topic_id]['obj'] = topic_data
                topic_db[topic_id]['best_answer_list'] = list()

                count = 0
                for answer in topic_data.best_answers:
                    ans_id = answer.id
                    topic_db[topic_id]['best_answer_list'].append(ans_id)
                    count += 1
                    max_count += 1

                    if ans_id not in answer_db:
                        answer_db[ans_id] = answer

                    if count > 1000:
                        break
                with open(ANSWER_DB_FILE, 'w') as f:
                    pickle.dump(answer_db, f)

                with open(TOPIC_DB_FILE, 'w') as f:
                    pickle.dump(topic_db, f)
            except (
                    GetDataErrorException,
                    requests.exceptions.ConnectionError):
                print("Error from server...")
                print("Saving Answer Database")
                with open(ANSWER_DB_FILE, 'w') as f:
                    pickle.dump(answer_db, f)
                    print(len(answer_db))

                print("Saving Topic Database")
                with open(TOPIC_DB_FILE, 'w') as f:
                    pickle.dump(topic_db, f)

                exit(0)

        print('Getting {0} answers...'.format(max_count))
        time.sleep(5)
        if max_count > 10000:
            with open(ANSWER_DB_FILE, 'w') as f:
                pickle.dump(answer_db, f)

            with open(TOPIC_DB_FILE, 'w') as f:
                pickle.dump(topic_db, f)
        exit(0)


if __name__ == '__main__':
    TOKEN_FILE = 'token.pkl'
    TOPIC_DB_FILE = 'topic_db.pkl'
    ANSWER_DB_FILE = 'answer_db.pkl'
    client = ZhihuClient()

    with open('topic_set', 'r') as fin:
        obj = pickle.load(fin)
    topic_db = get_dict_database(TOPIC_DB_FILE)
    answer_db = get_dict_database(ANSWER_DB_FILE)

    if os.path.isfile(TOKEN_FILE):
        client.load_token(TOKEN_FILE)
    else:
        client.login_in_terminal(use_getpass=False)
        client.save_token(TOKEN_FILE)
    get_essence_answer()
