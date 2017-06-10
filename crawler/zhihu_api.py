# -*- coding: utf-8 -*-

import json
import os.path
import re
import time
import urllib

import requests
from enum import Enum, unique

try:
    import cookielib
except ImportError:
    import http.cookiejar as cookielib

try:
    from PIL import Image
except ImportError:
    pass

from zhihu_settings import *

REQUEST_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
    'Referer': 'https://www.zhihu.com',
    'X-Requested-With': 'XMLHttpRequest',
    'Host': 'www.zhihu.com'
}

ZHUANLAN_REQUEST_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
    'Referer': 'https://www.zhihu.com',
    'X-Requested-With': 'XMLHttpRequest',
    'Host': 'zhuanlan.zhihu.com'
}


@unique
class UserAttrAPIStr(Enum):
    followees = 'followees'
    followers = 'followers'
    questions = 'questions'
    answers = 'answers'
    favor_lists = 'favlists'
    articles = 'articles'
    followed_topic = 'following-topic-contributions'
    followed_question = 'following-questions'
    publications = 'publications'


class ZhihuSession():
    def __init__(self):
        self.session = requests.session()
        self.cook_dict = dict()
        self.cook_dict_x = dict()
        self._xsrf = self.get_xsrf()
        self._header_with_xsrf = REQUEST_HEADERS
        self._header_with_xsrf['X-Xsrftoken'] = self._xsrf
        self.load_cookies()

    def get_xsrf(self):
        index_url = 'https://www.zhihu.com'
        index_page = self.session.get(index_url, headers=REQUEST_HEADERS)
        html = index_page.text
        pattern = r'name="_xsrf" value="(.*?)"'
        _xsrf = re.findall(pattern, html)
        return _xsrf[0]

    # 获取验证码
    def get_captcha(self):
        t = str(int(time.time() * 1000))
        captcha_url = 'https://www.zhihu.com/captcha.gif?r=' + t + "&type=login"
        r = self.session.get(captcha_url, headers=REQUEST_HEADERS)
        with open(CAPTCHA_PATH, 'wb') as f:
            f.write(r.content)
            f.close()
        try:
            im = Image.open(CAPTCHA_PATH)
            im.show()
            im.close()
        except:
            print(
                u'请到 %s 目录找到captcha.jpg 手动输入' % os.path.abspath(CAPTCHA_PATH))
        captcha = raw_input("Please input the captcha\n>")
        return captcha

    def is_login(self):
        url = 'http://www.zhihu.com/api/v4/members/lilian-31-77/publications' \
              '?limit=5&offset=0'
        login_code = self.session.get(url, headers=REQUEST_HEADERS, cookies=
        self.cook_dict).status_code

        if login_code == 200:
            return True
        else:
            return False

    def login(self):
        if os.path.exists(ACCOUNT_INFO_PATH):
            with open(ACCOUNT_INFO_PATH, 'r') as fin:
                account = fin.readline().strip()
                password = fin.readline().strip()
            print 'Email:', account
            print 'Password: ', '*' * len(password)
        else:
            account = raw_input('Email: ')
            password = raw_input('Password: ')

        if re.match(r"^1\d{10}$", account):
            print("手机号登录 \n")
            post_url = 'https://www.zhihu.com/login/phone_num'
            postdata = {
                '_xsrf': self._xsrf,
                'password': password,
                'phone_num': account
            }
        else:
            if "@" in account:
                print("邮箱登录 \n")
            else:
                print("你的账号输入有问题，请重新登录")
                return 0
            post_url = 'https://www.zhihu.com/login/email'
            postdata = {
                '_xsrf': self._xsrf,
                'password': password,
                'email': account
            }

        login_page = self.session.post(post_url, data=postdata,
                                       headers=self._header_with_xsrf)
        login_code = login_page.json()
        if login_code['r'] == 1:
            postdata["captcha"] = self.get_captcha()
            login_page = self.session.post(post_url, data=postdata,
                                           headers=self._header_with_xsrf)
            login_code = login_page.json()
            print(login_code['msg'])

        self.session.cookies.save()

    def load_cookies_file(self):
        if os.path.exists(COOKIES_PATH):
            self.session.cookies.load(ignore_discard=True)
            for i in list(self.session.cookies):
                self.cook_dict[i.name] = i.value

            self.cook_dict_x = self.cook_dict
            self.cook_dict_x['_xsrf'] = self._xsrf
            return True
        else:
            return False

    def load_cookies(self):
        self.session.cookies = cookielib.LWPCookieJar(filename=COOKIES_PATH)
        if self.load_cookies_file() and self.is_login():
            return True
        else:
            self.login()
            self.load_cookies_file()
            if self.is_login():
                return True
            else:
                print "Please check your password"
                exit(-1)

    # TODO check with 404 response
    def get_question_answer_list_raw(self, questionid, start, pagesize):
        return self.req_get(
            url='https://www.zhihu.com/node/QuestionAnswerListV2',
            headers=self._header_with_xsrf,
            data=urllib.urlencode({
                'method': 'next',
                'params': json.dumps({
                    'url_token': questionid,
                    'pagesize': pagesize,
                    'offset': start
                })
            }))

    def _get_userdata_api(self, section, user, start, pagesize):
        url = 'https://www.zhihu.com/api/v4/members/{0}/{1}?limit={2}&offset={3}'.format(
            user, section, pagesize, start)
        print url
        return requests.get(url=url, cookies=self.cook_dict,
                            headers=REQUEST_HEADERS).text

    def get_followees_raw(self, user, start, pagesize):
        return self._get_userdata_api(UserAttrAPIStr.followees.value, user,
                                      start, pagesize)

    def get_followers_raw(self, user, start, pagesize):
        return self._get_userdata_api(UserAttrAPIStr.followers.value, user,
                                      start, pagesize)

    def get_asked_questions_raw(self, user, start, pagesize):
        return self._get_userdata_api(UserAttrAPIStr.questions.value, user,
                                      start, pagesize)

    def get_answered_questions_raw(self, user, start, pagesize):
        return self._get_userdata_api(UserAttrAPIStr.answers.value, user,
                                      start, pagesize)

    def get_favourite_list_raw(self, user, start, pagesize):
        return self._get_userdata_api(UserAttrAPIStr.favor_lists.value, user,
                                      start, pagesize)

    def get_articles_raw(self, user, start, pagesize):
        return self._get_userdata_api(UserAttrAPIStr.articles.value, user,
                                      start, pagesize)

    def get_watched_topics_raw(self, user, start, pagesize):
        return self._get_userdata_api(UserAttrAPIStr.followed_topic.value,
                                      user,
                                      start, pagesize)

    def get_watched_questions_raw(self, user, start, pagesize):
        return self._get_userdata_api(UserAttrAPIStr.followed_question.value,
                                      user,
                                      start, pagesize)

    def get_publications_raw(self, user, start, pagesize):
        return self._get_userdata_api(UserAttrAPIStr.publications.value,
                                      user,
                                      start, pagesize)

    def get_all_userdata(self, user, has_follow):
        result = dict()
        for name, attr in UserAttrAPIStr.__members__.items():
            if not has_follow and (attr.value ==
                                       UserAttrAPIStr.followees.value
                                   or attr.value == UserAttrAPIStr.followers.value):
                continue
            print 'Crawling:', attr.value,
            result[attr.value] = dict()
            result[attr.value]['data'] = list()

            tmp_result = json.loads(self._get_userdata_api(section=attr.value,
                                                           start=0, user=user,
                                                           pagesize=20))
            try:
                print 'Total:', tmp_result['paging']['totals']
            except KeyError:
                print 'Total: 0'
            time.sleep(WAIT_TIME)

            if len(tmp_result['data']) != 0:
                result[attr.value]['num'] = tmp_result['paging']['totals']
                result[attr.value]['data'].extend(tmp_result['data'])
            else:
                result[attr.value]['num'] = 0

            while not tmp_result['paging']['is_end']:
                next_url = tmp_result['paging']['next']
                time.sleep(WAIT_TIME)
                print next_url
                try:
                    tmp_result = json.loads(
                        requests.get(url=next_url, cookies=self.cook_dict,
                                     headers=REQUEST_HEADERS).text)
                    result[attr.value]['data'].extend(tmp_result['data'])
                except requests.exceptions.ConnectionError:
                    print '\n\nError:', next_url
                    time.sleep(WAIT_TIME)
            print
        return result

    def get_article_content_raw(self, article):

        return self.req_get(
            url='https://zhuanlan.zhihu.com/api/posts/{0}'.format(article),
            headers=ZHUANLAN_REQUEST_HEADERS
        )

    # TODO Check with 404 response
    def get_question_watchers_raw(self, questionid, start):

        return self.req_get(
            url='https://www.zhihu.com/question/{0}/followers'.format(
                questionid),
            headers=self._header_with_xsrf,
            data=urllib.urlencode({
                'start': 0,
                'offset': start
            }), cookies=self.cook_dict_x
        )

    # Raw html
    def get_question_comments_raw(self, questionid):
        return self.req_get(
            url='https://www.zhihu.com/node/QuestionCommentListV2?params={{"question_id":{0}}}'.format(
                questionid))

    def get_answer_comments_raw(self, answerid, page):  # page starts from 1

        return self.req_get(
            url='https://www.zhihu.com/r/answers/{0}/comments?page={1}'.format(
                answerid, page))

    def get_article_comments_raw(self, articleid, start, pagesize):
        url = 'https://zhuanlan.zhihu.com/api/posts/{0}/comments?limit={1}&offset={2}'.format(
            articleid, pagesize, start)

        return requests.get(url=url, cookies=self.cook_dict,
                            headers=ZHUANLAN_REQUEST_HEADERS).text

    def get_children_topics(self, topicid, idafter=''):
        url = 'https://www.zhihu.com/topic/{0}/organize/entire?child={1}&parent={0}'.format(
            topicid, idafter)
        return self.req_get(url)

    def req_get(self, url, headers=None, data=None, cookies=None):

        if headers is None:
            headers = REQUEST_HEADERS

        if data is None:
            data = urllib.urlencode({
                '_xsrf': self._xsrf
            })

        if cookies is None:
            cookies = self.cook_dict
        try:
            result = requests.get(url, headers=headers,
                                  data=data, cookies=cookies).text
        except requests.exceptions.ConnectionError:
            print 'Bad url found, retry after {0}s'.format(
                str(ERROR_WAIT_TIME))
            time.sleep(ERROR_WAIT_TIME)
            result = requests.get(url, headers=headers,
                                  data=data, cookies=cookies).text
        return result

    @staticmethod
    def get_api_attr(url):
        return \
            url.split('www.zhihu.com/api/v4/members/')[1].split('?')[0].split(
                '/')[1]

    @staticmethod
    def get_user_attr_list():
        return [attr.value for name, attr in
                UserAttrAPIStr.__members__.items()]
