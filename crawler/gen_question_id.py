# Generate question id for parallel processing
import json
import os

import pickle

ANSWER_DB2_FILE = 'answer_db2.pkl'
if os.path.isfile(ANSWER_DB2_FILE):
    with open(ANSWER_DB2_FILE, 'r') as f:
        answer_db2 = pickle.load(f)
else:
    answer_db2 = dict()

QUESTION_DB_FILE = 'question_db.json'
with open(QUESTION_DB_FILE, 'r') as f:
    question_db = json.load(f)

print len(answer_db2)

question_id_set = set()

for a_id in answer_db2:
    q_id = unicode(answer_db2[a_id]['question'])
    if q_id not in question_db:
        question_id_set.add(q_id)

question_id_set = list(question_id_set)
length = len(question_id_set)

for i in range(6):
    with open('question_id_{0}'.format(i), 'w') as f:
        json.dump(question_id_set[i * length / 6:(i + 1) * length / 6], f)
