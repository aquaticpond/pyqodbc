
class Database:
    def __init__(self, db):
        self.db = db
        self.cursor = db.cursor()

    def disconnect(self):
        self.cursor.close()
        self.db.close()

    def query(self, sql):
        self.cursor.execute(sql)
        return self.cursor.fetchall()

    def insert(self, sql):
        self.cursor.execute(sql)
        self.db.commit()


