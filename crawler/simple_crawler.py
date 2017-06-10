import cPickle as pickle
import collections
import json
import time

from zhihu_api import ZhihuSession
from zhihu_settings import *

try:
    from win10toast import ToastNotifier
except ImportError:
    pass


class ZhihuCrawler:
    def __init__(self, using_database=True):
        self.database = dict()
        self.user_queue = collections.deque()
        self.load_data(using_database)
        self.load_user_queue(using_database)
        self.session = ZhihuSession()

        session = ZhihuSession()
        if not session.is_login():
            session.login()
        print 'login succeed'

    def crawl_people(self, root=None, curr_url=None, add_queue=True,
                     filter_V=False):
        attr_list = self.session.get_user_attr_list()

        if root is not None:
            self.user_queue.append(root)

        next_url = curr_url
        while True:
            # User has not been crawled ever
            attr_index = 0
            user_attr = attr_list[attr_index]
            if next_url is None:
                self.save_user_queue()
                id = self.user_queue.popleft()

                # this user has already crawled
                if id in self.database['user'] and 'all_data' in self.database[ \
                        'user'][id]:
                    continue
                if id not in self.database['user']:
                    self.database['user'][id] = dict()
                self.database['user'][id]['all_data'] = dict()
                print '\nCrawling:', id

                next_url = 'http://www.zhihu.com/api/v4/members/' \
                           '{0}/{1}?limit=20&offset=0'.format(
                    id, user_attr)
            else:
                print 'Restoring from previous state'
                user_attr = self.session.get_api_attr(next_url)
                attr_index = attr_list.index(user_attr)
                id = root

            retry_count = 0
            while True:
                self.save_current_url(next_url)
                try:
                    url_response = json.loads(self.session.req_get(next_url))
                    retry_count = 0
                except:
                    self.save_user_queue()
                    self.save_data()
                    self.save_current_url(next_url)
                    retry_count += 1
                    self.notifier('Zhihu Crawler',
                                  '{0} is in a error state'.format(
                                      next_url))

                    if retry_count > 3:
                        self.notifier('Zhihu Crawler', 'Exit due to '
                                                       'previous error '
                                                       'state')
                        exit(-1)
                    continue

                if url_response['paging']['is_start']:
                    print '\nCrawling', user_attr,
                    self.database['user'][id]['all_data'][
                        user_attr] = dict()
                    try:
                        self.database['user'][id]['all_data'][user_attr][
                            'num'] = url_response['paging']['totals']
                    except KeyError:
                        self.database['user'][id]['all_data'][user_attr][
                            'num'] = 0

                    print 'Total:', self.database['user'][id]['all_data'][
                        user_attr]['num']

                    self.database['user'][id]['all_data'][user_attr][
                        'data'] = list()

                if self.database['user'][id]['all_data'][user_attr][
                    'num'] > 5000:
                    print 'Too much url, do it later'

                    if attr_index == len(attr_list) - 1:
                        next_url = None
                        break
                    else:
                        attr_index += 1
                        user_attr = attr_list[attr_index]
                        next_url = 'http://www.zhihu.com/api/v4/members/' \
                                   '{0}/{1}?limit=20&offset=0'.format(
                            id, user_attr)
                        continue


                print next_url
                current_attr_list = \
                    self.database['user'][id]['all_data'][user_attr][
                        'data']
                # Check if current user follow list should be added to user
                # queue

                if user_attr == 'followers' or user_attr == 'followees':
                    for people in url_response['data']:
                        id_to_crawl = people['url_token']
                        current_attr_list.append(id_to_crawl)
                        if id_to_crawl not in self.database['user']:
                            self.database['user'][id_to_crawl] = dict()
                            self.database['user'][id_to_crawl][
                                'simple_description'] = people
                            if add_queue:
                                self.user_queue.append(id_to_crawl)

                else:
                    current_attr_list.extend(url_response['data'])


                time.sleep(WAIT_TIME)

                if url_response['paging']['is_end']:
                    if attr_index == len(attr_list) - 1:
                        next_url = None
                        break
                    else:
                        attr_index += 1
                        user_attr = attr_list[attr_index]
                        next_url = 'http://www.zhihu.com/api/v4/members/' \
                                   '{0}/{1}?limit=20&offset=0'.format(
                            id, user_attr)
                else:
                    next_url = url_response['paging']['next']

            self.save_data()
            self.save_user_queue()

            if len(self.user_queue) == 0:
                break

    def save_data(self):
        with open(USER_DATABASE_PATH, 'w') as f:
            pickle.dump(self.database['user'], f)

    def save_user_queue(self):
        with open(USER_QUEUE_PATH, 'w') as f:
            pickle.dump(self.user_queue, f)

    def save_current_url(self, url):
        with open(CURRENT_URL_PATH, 'w') as f:
            f.write(url)

    def load_data(self, using_database):
        if os.path.exists(USER_DATABASE_PATH) and \
                using_database:
            print 'Loading database from local file...'
            with open(USER_DATABASE_PATH, 'r') as f:
                self.database['user'] = pickle.load(f)
                print 'Completed!'
        else:
            self.database['user'] = dict()

    def load_user_queue(self, using_database):
        if os.path.exists(USER_QUEUE_PATH) and using_database:
            print 'Loading user queue from local file...'
            with open(USER_QUEUE_PATH, 'r') as f:
                self.user_queue = pickle.load(f)
                print 'Completed!'

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
