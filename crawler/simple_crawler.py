import collections
import json
import os
import pickle
import time

from zhihu_api import ZhihuSession
from zhihu_settings import *


class ZhihuCrawler:
    def __init__(self):
        self.database = dict()
        self.user_queue = collections.deque()
        self.load_data()
        self.load_user_queue()
        self.session = ZhihuSession()

        session = ZhihuSession()
        if not session.is_login():
            session.login()
        print 'login succeed'

    def crawl_people(self, root=None):
        if root is not None:
            self.user_queue.append(root)
            self.database['user'][root] = dict()

        count = 0
        while not len(self.user_queue) == 0:
            if count > 20:
                self.save_user_queue()
                self.save_data()
                return
            count += 1
            id = self.user_queue.popleft()
            print 'Crawling:', id

            self.database['user'][id]['all_data'] = \
                self.session.get_all_userdata(id)
            self.save_data()
            self.save_user_queue()
            print 'Userdata of {0} added'.format(id)

            followers = json.loads(self.session.get_followers_raw(id, 0, 20))

            while not followers['paging']['is_end']:
                next_url = followers['paging']['next']
                print next_url
                for people in followers['data']:
                    id_to_crawl = people['url_token']
                    if id_to_crawl not in self.database['user']:
                        self.database['user'][id_to_crawl] = dict()
                        self.database['user'][id_to_crawl][
                            'simple_description'] = people
                        self.user_queue.append(id_to_crawl)
                time.sleep(WAIT_TIME)
                followers = json.loads(self.session.req_get(next_url))

            followees = json.loads(self.session.get_followees_raw(id, 0, 20))
            while not followees['paging']['is_end']:
                next_url = followees['paging']['next']
                print next_url
                for people in followees['data']:
                    id_to_crawl = people['url_token']
                    if id_to_crawl not in self.database['user']:
                        self.database['user'][id_to_crawl] = dict()
                        self.database['user'][id_to_crawl][
                            'simple_description'] = people
                        self.user_queue.append(id_to_crawl)
                time.sleep(WAIT_TIME)
                followees = json.loads(self.session.req_get(next_url))

    def save_data(self):
        with open('data', 'w') as f:
            pickle.dump(self.database, f)

    def save_user_queue(self):
        with open('user_queue', 'w') as f:
            pickle.dump(self.user_queue, f)

    def load_data(self):
        if os.path.exists('data'):
            with open('data', 'r') as f:
                self.database = pickle.load(f)
        else:
            self.database['user'] = dict()

    def load_user_queue(self):
        if os.path.exists('user_queue'):
            with open('user_queue', 'r') as f:
                self.user_queue = pickle.load(f)

    @staticmethod
    def bfs():
        pass
