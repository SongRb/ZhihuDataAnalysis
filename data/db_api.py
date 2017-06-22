import psycopg2

from db_settings import *


class PostgresProvider:
    def __init__(self):
        self.passwd = PASSWD
        self.db_name = DBNAME
        self.username = USERNAME
        self.host = HOST
        self.cursor = None

    def connect(self):
        conn = psycopg2.connect(
            "dbname='{0}' user='{1}' host='{2}' password='{3}'".format(
                self.db_name, self.username, self.host, self.passwd)
        )
        conn.autocommit = True
        self.cursor = conn.cursor()

    def execute(self, command):
        # print command
        try:
            self.cursor.execute(command)
        except Exception as e:
            print e
            print command
        try:
            return self.cursor.fetchall()
        except psycopg2.ProgrammingError:
            return None

    # Require a tuple containing value to be queried in str
    # Require a str identifies table name
    def select_from_table(self, values, tb_name, limit=None):
        if not isinstance(values, tuple) or not isinstance(tb_name, str):
            raise TypeError
        value_string = ''
        for value in values:
            if isinstance(value, str):
                value_string += value
                value_string += ','
            else:
                raise TypeError

        value_string = value_string.rstrip(',')
        if limit is None:
            return self.execute(
                'SELECT {0} FROM {1}'.format(value_string, tb_name))
        else:
            return self.execute('SELECT {0} FROM {1} LIMIT {2}'.format(
                value_string, tb_name, limit))

    # TODO Implement Non-Duplicate Option
    def add_value(self, data, tb_name):

        key_string, value_string = self.clean_string(data)

        command = u"""INSERT INTO {0} ({1}) VALUES ({2})""".format(tb_name,
                                                                   key_string,
                                                                   value_string)
        # if not allow_dup:
        #     command+=u"""ON CONFLICT UPDATE"""

        self.execute(command)

    def update_value(self, data, condition, tb_name):
        key_value_string = ''

        for key in data:
            key_value_string += """{0} = {1},""".format(unicode(key),
                                                        self.convert_string(
                                                            data[key]))
        key_value_string = key_value_string.rstrip(',')

        condition_string = condition

        command = u"""UPDATE {0} SET {1} WHERE {2}""".format(tb_name,
                                                             key_value_string,
                                                             condition_string)

        self.execute(command)

    def create_table(self, keys, tb_name):
        value_string = ''
        for key in keys:
            for key_item in key:
                value_string += key_item
                value_string += ' '
            value_string += ','

        value_string = value_string.rstrip(',')

        self.execute('CREATE TABLE {0} ({1});'.format(tb_name, value_string))

    def delete_table(self, tb_name):
        self.execute('DROP TABLE IF EXISTS {0}  '.format(tb_name))

    @staticmethod
    def clean_character(token):
        # Backslash
        token = token.replace("""\\""", """\\\\""")
        token = token.replace("'", r"''")
        return token

    def convert_string(self, token):
        if isinstance(token, str) or isinstance(token, unicode):
            if len(token) != 0:
                return u"U&'{0}',".format(
                    self.clean_character(unicode(token))
                )
            else:
                return u'null,'
        elif isinstance(token, bool):
            return u'{0},'.format(u'true' if token else u'false')
        else:
            return u'{0},'.format(self.clean_character(unicode(token)))

    def clean_string(self, data):
        key_string = u''
        value_string = u''
        for key in data:
            key_string += u'{0},'.format(unicode(key))
            value_string += self.convert_string(data[key])

        return key_string.rstrip(u','), value_string.rstrip(u',')
