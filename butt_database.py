import MySQLdb
from MySQLdb.cursors import DictCursor


class Db:
    def __init__(self, _db, username, password, test_environment):
        self._db = _db
        self.user = username
        self.passw = password
        self.test_environment = test_environment

    def build(self):
        self.connection = MySQLdb.connect(host='127.0.0.1', user=self.user, passwd=self.passw, db=self._db,
                                          cursorclass=DictCursor)

    def do_query(self, query, args=''):
        self.build()
        try:
            with self.connection.cursor() as cursor:
                # Read a single record
                if args:
                    cursor.execute(query, args)
                else:
                    cursor.execute(query)
                result = cursor.fetchall()
                cursor.close()
        finally:
            pass
        return result

    def do_insert(self, query, args):
        self.build()
        try:
            with self.connection.cursor() as cursor:
                print("executing query: %s with arguments %s" % (query, args))
                cursor.execute(query, args)
                self.connection.commit()
                cursor.close()
        finally:
            pass

    def close(self):
        self.connection.close()

    def do_insertmany(self, query, args):
        self.build()
        with self.connection.cursor() as cursor:
            try:
                print("executing manyquery: %s with arguments %s" % (query, args))
                cursor.executemany(query, args)
                self.connection.commit()
                cursor.close()
            except:
                print("Error executing this mysql query: %s" % cursor._last_executed)
                raise
            finally:
                pass
