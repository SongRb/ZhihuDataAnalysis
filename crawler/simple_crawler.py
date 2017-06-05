import collections
import json
import os
import pickle
import time

from zhihu_api import ZhihuSession
from zhihu_settings import *

try:
    from win10toast import ToastNotifier
except ImportError:
    pass


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

    def crawl_people(self, root=None, curr_url=None):
        if root is not None:
            self.user_queue.append(root)
            self.database['user'][root] = dict()

        count = 0
        while not len(self.user_queue) == 0:
            if count > 10:
                self.save_user_queue()
                self.save_data()
                return
            count += 1
            if curr_url is None:
                self.save_user_queue()
                id = self.user_queue.popleft()
                print 'Crawling:', id
                if id in self.database['user'] and 'all_data' in self.database[ \
                        'user'][id]:
                    continue
                self.database['user'][id]['all_data'] = \
                    self.session.get_all_userdata(id, has_follow=False)
                self.save_data()

            print 'Starting crawling next people process: '
            if curr_url is None or 'followers' in curr_url:
                if curr_url is None:
                    followers = json.loads(
                        self.session.get_followers_raw(id, 0, 20))
                    self.database['user'][id]['all_data']['followers'] = dict()
                    self.database['user'][id]['all_data']['followers']['num'] = \
                        followers['paging']['totals']
                    self.database['user'][id]['all_data']['followers'][
                        'data'] = list()
                    all_followers = \
                        self.database['user'][id]['all_data']['followers'][
                            'data']
                else:
                    followers = json.loads(self.session.req_get(curr_url))
                retry_count = 0
                while True:
                    next_url = followers['paging']['next']

                    for people in followers['data']:
                        id_to_crawl = people['url_token']
                        all_followers.append(id_to_crawl)
                        if id_to_crawl not in self.database['user']:
                            self.database['user'][id_to_crawl] = dict()
                            self.database['user'][id_to_crawl][
                                'simple_description'] = people
                            self.user_queue.append(id_to_crawl)
                    time.sleep(WAIT_TIME)
                    if followers['paging']['is_end']:
                        break
                    print next_url
                    try:
                        followers = json.loads(self.session.req_get(next_url))
                        retry_count = 0
                    except:
                        self.save_user_queue()
                        self.save_data()
                        self.save_current_url(next_url)
                        retry_count += 1
                        self.notifier('Zhihu Crawler', '{0} is in a error '
                                                       'state'.format(
                            next_url))
                        if retry_count > 3:
                            self.notifier('Zhihu Crawler', 'Exit due to '
                                                           'previous error '
                                                           'state')
                            exit(-1)

            self.save_user_queue()
            self.save_data()

            if curr_url is None or 'followees' in curr_url:
                if curr_url is None:
                    followees = json.loads(
                        self.session.get_followees_raw(id, 0, 20))
                    self.database['user'][id]['all_data']['followees'] = dict()
                    self.database['user'][id]['all_data']['followees']['num'] = \
                        followees['paging']['totals']
                    self.database['user'][id]['all_data']['followees'][
                        'data'] = list()
                    all_followees = \
                        self.database['user'][id]['all_data']['followees'][
                            'data']
                else:
                    followees = json.loads(self.session.req_get(curr_url))
                retry_count = 0
                while True:
                    next_url = followees['paging']['next']

                    for people in followees['data']:
                        id_to_crawl = people['url_token']
                        all_followees.append(id_to_crawl)
                        if id_to_crawl not in self.database['user']:
                            self.database['user'][id_to_crawl] = dict()
                            self.database['user'][id_to_crawl][
                                'simple_description'] = people
                            self.user_queue.append(id_to_crawl)
                    time.sleep(WAIT_TIME)
                    if followees['paging']['is_end']:
                        break
                    print next_url
                    try:
                        followees = json.loads(self.session.req_get(next_url))
                        retry_count = 0
                    except:
                        self.save_user_queue()
                        self.save_data()
                        self.save_current_url(next_url)
                        retry_count += 1
                        self.notifier('Zhihu Crawler', '{0} is in a error '
                                                       'state'.format(
                            next_url))
                        if retry_count > 3:
                            self.notifier('Zhihu Crawler', 'Exit due to '
                                                           'previous error '
                                                           'state')
                            exit(-1)

            self.save_user_queue()
            self.save_data()

            print 'Userdata of {0} added'.format(id)

    def save_data(self):
        with open('data', 'w') as f:
            pickle.dump(self.database, f)

    def save_user_queue(self):
        with open('user_queue', 'w') as f:
            pickle.dump(self.user_queue, f)

    def save_current_url(self, url):
        with open('current_url', 'w') as f:
            f.write(url)

    def load_data(self):
        if os.path.exists('data'):
            print 'Loading database from local file...'
            with open('data', 'r') as f:
                self.database = pickle.load(f)
                print 'Completed!'
        else:
            self.database['user'] = dict()

    def load_user_queue(self):
        if os.path.exists('user_queue'):
            print 'Loading user queue from local file...'
            with open('user_queue', 'r') as f:
                self.user_queue = pickle.load(f)
                print 'Completed!'

    @staticmethod
    def bfs():
        pass

    @staticmethod
    def notifier(title, message):
        try:
            toaster = ToastNotifier()
            toaster.show_toast(title, message,
                               icon_path="custom.ico",
                               duration=10)
        except:
            pass
        print message
