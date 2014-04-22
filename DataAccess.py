from bson import Code
from pymongo import Connection
from pymongo.database import Database

__author__ = 'manuel'


class ConfigDB:
    def __init__(self):
        self.__connection = Connection(host="localhost")
        self.__db = Database(connection=self.__connection, name="broadcaster_dev")

    def get_collection(self, collection, where={}):
        return self.__db[collection].find(spec=where)

    def get_document(self, collection, where={}):
        return self.__db[collection].find_one(spec_or_id=where)

    def get_tuple(self, collection, text, value="_id", where={}):
        l = []
        for i in list(self.__db[collection].find(spec=where)):
            l += [(i[value], i[text])]
        return tuple(l)

    def set_campaign(self, _id, values):
        q = {}
        if _id is not None:
            q = {"_id", _id}
        return self.__db["campaigns"].find_and_modify(
            query=q,
            update=values,
            upsert=True,
            new=True
        )

    def set_document(self, collection, _id, values):
        return self.__db[collection].find_and_modify(
            query={"_id": _id},
            update=values,
            upsert=True,
            new=True
        )

    def get_categories(self):
        return self.get_tuple(
            collection="categories",
            text="name"
        )

    def get_products(self):
        return self.get_tuple(
            collection="products",
            text="name"
        )

    def get_priorities(self):
        return self.get_tuple(
            collection="priorities",
            text="label"
        )

    def get_users(self, role):
        return self.get_tuple(
            collection="users",
            text="user_name",
            where={"role": role}
        )

    def get_destinations(self):
        return self.get_tuple(
            collection="destenations",
            text="dial"
        )

    def get_whitelists(self):
        return self.get_tuple(
            collection="lists",
            text="name",
            where={"type": "white"}
        )

    def get_blacklists(self):
        return self.get_tuple(
            collection="lists",
            text="name",
            where={"type": "black"}
        )

    def exists_collection(self, name):
        return name in self.__db.collection_names()

    def get_active_campaigns(self, day):
        pass

class DataDB:

    def __init__(self, name):
        self.__db_name = "camp" + name
        self.__connection = Connection(host="localhost")
        self.__db = Database(connection=self.__connection, name=self.__db_name)

    def drop_collection(self, collection):
        self.__db[collection].drop()

    def bulk_import(self, collection, doc_or_docs):
        self.__db[collection].insert(doc_or_docs)

    def move_unique(self, source, destenation, order="as it is"):
        map = Code("function () {"
                   "    if (db.blacklist.find({'number':this._id}).count() == 0) {"
                   "        emit(this._id, 1);"
                   "    }"
                   "}")

        reduce = Code("function (key, values) {"
                      "  return key;"
                      "}")

        self.__db[destenation].drop()
        self.__db[source].map_reduce(map=map, reduce=reduce, out=destenation)

