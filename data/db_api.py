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
        self.cursor = conn.cursor()

    def execute(self, command):
        print command
        self.cursor.execute(command)
        try:
            return self.cursor.fetchall()
        except psycopg2.ProgrammingError:
            return None

    # Require a tuple containing value to be queried in str
    # Require a str identifies table name
    def select_from_table(self, values, tb_name):
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
        return self.execute(
            'SELECT {0} FROM {1}'.format(value_string, tb_name))

    def add_value(self, data, tb_name):
        key_string = ''
        value_string = ''
        for key in data:
            key_string += '{0},'.format(str(key))

            if isinstance(data[key], str) or isinstance(data[key], unicode):
                if len(data[key]) != 0:
                    value_string += "'{0}',".format(data[key])
                else:
                    value_string += 'null,'
            elif isinstance(data[key], bool):
                value_string += '{0},'.format('true' if data[key] else 'false')
            else:
                value_string += '{0},'.format(str(data[key]))

        key_string = key_string.rstrip(',')
        value_string = value_string.rstrip(',')

        command = """INSERT INTO {0} ({1}) VALUES ({2})""".format(tb_name,
                                                                  key_string,
                                                                  value_string)

        print command

    # self.execute(command)


    def create_table(self, keys, tb_name):
        value_string = ''
        for key in keys:
            value_string += '{0} {1},'.format(key[0], key[1])

        value_string = value_string.rstrip(',')

        self.execute('CREATE TABLE {0} ({1});'.format(tb_name, value_string))

    def delete_table(self, tb_name):
        self.execute('DROP TABLE IF EXISTS {0}  '.format(tb_name))
