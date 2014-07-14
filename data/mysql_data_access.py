import MySQLdb
from im.core.config import conf

__author__ = 'manuel'


class AuthenticationDB:

    def __init__(self):
        host = conf("mysql.host")
        port = conf("mysql.port")
        usr = conf("mysql.default_username")
        pwd = conf("mysql.default_password")
        db = conf("mysql.databases.default")

        self.__db = MySQLdb.connect(host="" if host is None else host,
                                    port="" if port is None else port,
                                    user="" if usr is None else usr,
                                    passwd="" if pwd is None else pwd,
                                    db="" if db is None else db)

    # Converts the cursor to a list of dictionaries.
    def parse_cursor(self, cursor, columns=[]):
        result = []
        for row in cursor:
            result_row = {}
            for c in columns:
                result_row.setdefault(c, row[len(result_row)])
            result += [result_row]
        return result

    # Get the complete list of groups for dropdown options.
    def get_groups(self):
        cur = self.__db.cursor()
        cur.execute("SELECT id, name "
                    "FROM auth_group")
        return cur

    # Get users list.
    def get_users(self):
        cur = self.__db.cursor()
        cur.execute("SELECT id, username, first_name, last_name, last_login "
                    "FROM auth_user "
                    "ORDER BY username")
        return self.parse_cursor(cur, ["id", "username", "first_name", "last_name", "last_login"])

    # Get the user complete profile.
    def get_user(self, user_id):
        cur = self.__db.cursor()

        # Get user data.
        cur.execute("SELECT id, username, first_name, last_name, email, last_login "
                    "FROM auth_user "
                    "WHERE id = {0}".format(user_id))

        # Parse the cursor.
        result = self.parse_cursor(cur, ["id", "username", "first_name", "last_name", "email", "last_login"])

        # Get the groups.
        cur.execute("SELECT group_id "
                    "FROM auth_user_groups "
                    "WHERE user_id = {0}".format(user_id))
        groups = []
        for g in cur:
            groups += [g[0]]

        # Add groups to the user profile.
        result[0]["groups"] = groups

        return result[0]