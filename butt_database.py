import MySQLdb
from MySQLdb.cursors import DictCursor
import logging

log = logging.getLogger('bot.' + __name__)


class Db:
    def __init__(self, _db: str, username: str, password: str):
        self._db = _db
        self.user = username
        self.passw = password
        self.connection = MySQLdb.connect(host='127.0.0.1', user=self.user, passwd=self.passw, db=self._db,
                                          cursorclass=DictCursor)

    def do_query(self, query, args=''):
        log.debug("QUERY - executing query %s with args %s" % (query, args))
        try:
            with self.connection.cursor() as cursor:
                # Read a single record
                if args:
                    cursor.execute(query, args)
                else:
                    cursor.execute(query)
                result = cursor.fetchall()
        finally:
            pass
        return result

    def do_insert(self, query, args):
        log.debug("INSERT - executing query %s with args %s" % (query, args))
        try:
            with self.connection.cursor() as cursor:
                log.debug("executing query: %s with arguments %s" % (query, args))
                cursor.execute(query, args)
                self.connection.commit()
        finally:
            pass

    def do_insert_no_args(self, query):
        log.debug("INSERT_NO_ARGS - executing query %s" % (query))
        try:
            with self.connection.cursor() as cursor:
                log.info("running query: %s" % str(query))
                cursor.execute(query)
                self.connection.commit()
        finally:
            pass

    def close(self):
        self.connection.close()

    def do_insertmany(self, query, args):
        log.debug("INSERTMANY - executing query %s with args %s" % (query, args))
        with self.connection.cursor() as cursor:
            try:
                log.debug("executing manyquery: %s with arguments %s" % (query, args))
                cursor.executemany(query, args)
                self.connection.commit()
            except:
                log.critical("Error executing this mysql query: %s" % cursor._last_executed)
                raise
            finally:
                pass
