from bson import Code
from pymongo import Connection
from pymongo.database import Database
from im.core.config import conf

__author__ = 'manuel'


class ConfigDB:
    def __init__(self):
        db_server_ip = conf("config.db_server_ip")
        db_server_port = conf("config.db_server_port")
        self.__connection = Connection(host=db_server_ip, port=db_server_port)

        db_name = conf("config.db_name")
        self.__db = Database(connection= self.__connection, name=db_name)


    # Returns a tuple with paired values to be used in drop down lists.
    def get_tuple(self, collection, text, value="_id", where={}):
        l = []
        for i in list(self.__db[collection].find(spec=where)):
            l += [(i[value], i[text])]
        return tuple(l)


    # Moves unique records from source collection to destination, order parameter still pending.
    def move_unique(self, source, destination):
        map_func = Code(
            "function () {"
            "   emit(this._id, 1);"
            "}")
        reduce_func = Code(
            "function (key, values) {"
            "  return key;"
            "}")
        self.__db[destination].drop()
        self.__db[source].map_reduce(map=map_func, reduce=reduce_func, out=destination)

    # Return collection with the specified name and filter.
    def get_collection(self, collection, where={}):
        return self.__db[collection].find(spec=where)

    # Returns the first document that matches the where clause within the specified collection.
    def get_document(self, collection, where={}):
        return self.__db[collection].find_one(spec_or_id=where)


    # Removes the specified document.
    def dispose_document(self, collection, where):
        return self.__db[collection].remove(spec_or_id=where)

    # Updates the document with the specified id, the document is inserted if the _id is not found.
    # Returns the updated document.
    def set_document(self, collection, _id, values):
        if _id is None:
            # If no _id to update, insert it.
            _id = self.__db[collection].insert(values)
        else:
            # If _id to update, update it.
            self.__db[collection].update(
                spec={"_id": _id},
                document={"$set": values},
                upsert=True,
                new=True)
        # Return modified document.
        return self.__db[collection].find_one({"_id": _id})

    # Removes the specified collection from the database.
    def dispose_collection(self, collection):
        self.__db[collection].drop()


    # Insert a bulk of documents into a collection.
    def bulk_import(self, collection, doc_or_docs):
        self.__db[collection].insert(doc_or_docs)

    # Return the count of documents for a specific collection.
    def count_documents(self, collection, where={}):
        cur = self.__db[collection].find(where)
        return cur.count()

    def exists_collection(self, name):
        return name in self.__db.collection_names()

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
            collection="destinations",
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


class DataDB:

    def __init__(self, name):
        db_server_ip = conf("config.db_server_ip")
        db_server_port = conf("config.db_server_port")
        self.__db_name = "camp" + name
        self.__connection = Connection(host=db_server_ip, port=db_server_port)
        self.__db = Database(connection= self.__connection, name=self.__db_name)

        # Return collection with the specified name and filter.
    def get_collection(self, collection, where={}):
        return self.__db[collection].find(spec=where)

    # Returns the first document that matches the where clause within the specified collection.
    def get_document(self, collection, where={}):
        return self.__db[collection].find_one(spec_or_id=where)


    # Removes the specified document.
    def dispose_document(self, collection, where):
        return self.__db[collection].remove(spec_or_id=where)

    # Updates the document with the specified id, the document is inserted if the _id is not found.
    # Returns the updated document.
    def set_document(self, collection, _id, values):
        if _id is None:
            # If no _id to update, insert it.
            _id = self.__db[collection].insert(values)
        else:
            # If _id to update, update it.
            self.__db[collection].update(
                spec={"_id": _id},
                document={"$set": values},
                upsert=True,
                new=True)
        # Return modified document.
        return self.__db[collection].find_one({"_id": _id})

    # Removes the specified collection from the database.
    def dispose_collection(self, collection):
        self.__db[collection].drop()


    # Insert a bulk of documents into a collection.
    def bulk_import(self, collection, doc_or_docs):
        self.__db[collection].insert(doc_or_docs)

    # Return the count of documents for a specific collection.
    def count_documents(self, collection, where={}):
        cur = self.__db[collection].find(where)
        return cur.count()

    def exists_collection(self, name):
        return name in self.__db.collection_names()

    # Moves unique records from source collection to destination, order parameter still pending.
    def perform_cleanup(self, source, destination, order="as it is"):
        map_func = Code(
            "function () {"
            #"    if (db.blacklist.find({'_id':this._id}).count() == 0) {"
            "        emit(this._id, 1);"
            #"    }"
            "}")
        reduce_func = Code(
            "function (key, values) {"
            "  return key;"
            "}")
        self.__db[destination].drop()
        self.__db[source].map_reduce(map=map_func, reduce=reduce_func, out=destination)
