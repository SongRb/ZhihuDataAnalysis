import os
import pickle
import time

from zhihu_oauth import ZhihuClient

QUESTION_DB_FILE = 'question_db.pkl'
TOPIC_DB2_FILE = 'topic_db2.pkl'


def get_dict_database(filename):
    if os.path.isfile(filename):
        with open(filename, 'r') as f:
            return pickle.load(f)
    else:
        return dict()


question_db = get_dict_database(QUESTION_DB_FILE)
topic_db2 = get_dict_database(TOPIC_DB2_FILE)

client = ZhihuClient()
TOKEN_FILE = 'token.pkl'
if os.path.isfile(TOKEN_FILE):
    client.load_token(TOKEN_FILE)
else:
    client.login_in_terminal(use_getpass=False)
    client.save_token(TOKEN_FILE)

cnt = 0
for q_id in question_db:
    try:
        if len(question_db[q_id]) == 0:
            print 'Crawling', q_id
            question = client.question(q_id)
            question_db[q_id] = {
                'answer_count': question.answer_count,
                'comment_count': question.comment_count,
                'created_time': question.created_time,
                'follower_count': question.follower_count,
                'detail': question.detail,
                'title': question.title,
                'updated_time': question.updated_time,
            }
            cnt += 1

            if cnt % 100 == 0:
                with open(QUESTION_DB_FILE, 'w') as f:
                    pickle.dump(question_db, f)

                with open(TOPIC_DB2_FILE, 'w') as f:
                    pickle.dump(topic_db2, f)

            if cnt % 200 == 0:
                print('Sleeping...')
                time.sleep(10)

            time.sleep(2)

            question_db[q_id]['topics'] = list()
            for topic in question.topics:
                question_db[q_id]['topics'].append(topic.index.id)
                if topic.index.id not in topic_db2:
                    topic_db2[topic.index.id] = {
                        'best_answer_count': topic.best_answer_count,
                        'best_answers_count': topic.best_answers_count,
                        'father_count': topic.father_count,
                        'follower_count': topic.follower_count,
                        'followers_count': topic.followers_count,
                        'introduction': topic.introduction,
                        'name': topic.name,
                        'parent_count': topic.parent_count,
                        'question_count': topic.question_count,
                        'questions_count': topic.questions_count,
                        'unanswered_count': topic.unanswered_count
                    }

            with open(QUESTION_DB_FILE, 'w') as f:
                pickle.dump(question_db, f)

            with open(TOPIC_DB2_FILE, 'w') as f:
                pickle.dump(topic_db2, f)

    except:
        print 'Saving State...'
        print 'Error occurred in', q_id
        with open(QUESTION_DB_FILE, 'w') as f:
            pickle.dump(question_db, f)

        with open(TOPIC_DB2_FILE, 'w') as f:
            pickle.dump(topic_db2, f)
