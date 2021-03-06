import pymysql
import time

class Entity:

    qodbc_table = None
    mysql_table = None
    mysql_legacy_key = None
    qodbc_legacy_key = None
    field_map = ()
    update_fields = ()
    custom_mysql_fields = ()
    last_entry_datetime = None
    company_file = 0

    def __init__(self, qodbc, mysql, company_file=0, last_modified=None):
        self.qodbc = qodbc
        self.mysql = mysql
        self.company_file = company_file or self.company_file
        self.last_entry_datetime = last_modified or self.last_entry_datetime or self.get_last_modified() or '2001-01-01 00:00:00'

    def append_custom_data(self, toRaw):
        return toRaw

    def sync(self):
        data = self.get_latest_data_from_quickbooks()
        data = self.append_custom_data(data)
        self.write_batch(data)

    def sync_where(self, where):
        data = self.get_data_from_quickbooks_where(where)
        data = self.append_custom_data(data)
        self.write_batch(data)

    def update_legacy(self, fromDate):
        query = "SELECT " + self.mysql_legacy_key + " FROM " + self.mysql_table + " WHERE time_modified > {ts '" + fromDate + "'} GROUP BY " + self.mysql_legacy_key
        results = self.mysql.query(query)
        [self.update_legacy_record(row[0]) for row in results]

    def update_legacy_record(self, record_id):
        query = "SELECT " + self.build_quickbooks_select_fields() + " FROM " + self.qodbc_table + " WHERE " + self.qodbc_legacy_key + " = '" + record_id + "'"
        legacy = self.qodbc.query(query)
        legacy = self.append_custom_data(legacy)
        self.write_batch(legacy)

    def write_batch(self, data):
        for record in data:
            self.write_record(record)

    def write_record(self, record):
        try:
            insert = self.build_mysql_insert(record)
            print(record)
            print(insert)
            self.mysql.insert(insert)
        except pymysql.Error as error:
            print("exception handled")
            self.log_query_error(str(error), str(record), insert)

    def get_last_modified(self):
        query = "SELECT MAX(time_modified) as max_date FROM " + self.mysql_table + " WHERE company_file=" + self.company_file + " AND time_created <= NOW() + INTERVAL 4 HOUR"
        result = self.mysql.query(query)
        if result[0] and result[0][0]:
            return str(result[0][0])

        return None

    def get_latest_data_from_quickbooks(self):
        query = "SELECT " + self.build_quickbooks_select_fields() + " FROM " + self.qodbc_table + " WHERE TimeModified >= {ts '" + self.last_entry_datetime +"'}"
        return self.qodbc.query(query)

    def get_data_from_quickbooks_where(self, where):
        query = "SELECT " + self.build_quickbooks_select_fields() + " FROM " + self.qodbc_table + " WHERE "+ where
        return self.qodbc.query(query)

    def build_quickbooks_select_fields(self):
        fields = [map[0] + " AS " + map[1] for map in self.field_map]
        return ', '.join(fields)

    def build_mysql_insert_fields(self):
        fields = [each[1] for each in self.field_map]
        custom = [each for each in self.custom_mysql_fields]
        return ', '.join(fields + custom)

    def build_mysql_insert_values(self, data):
        values = [self.mysql.db.escape(value) for value in data]
        return ', '.join(values)

    def build_mysql_insert_on_duplicate_key_update(self):
        updates = [field + '=VALUES(' + field + ')' for field in self.update_fields]
        return ', '.join(updates)

    def build_mysql_insert(self, data):
        fields = self.build_mysql_insert_fields()
        values = self.build_mysql_insert_values(data)
        on_dupe = self.build_mysql_insert_on_duplicate_key_update()

        return 'INSERT INTO ' + self.mysql_table + ' (' + fields + ') VALUES(' + values + ') ON DUPLICATE KEY UPDATE ' + on_dupe

    def describe_quickbooks_table(self):
        return self.qodbc.query("sp_columns " + self.qodbc_table)

    def debug_quickbooks_table(self):
        [print(data) for data in self.describe_quickbooks_table()]

    def log_query_error(self, error, data, query):
        file = open('log.txt', 'a')
        file.write(time.strftime("%Y-%m-%d %H:%M:%S") + "\n")
        file.write(error + "\n")
        file.write(data + "\n")
        file.write(query + "\n")
        file.write("\n")
        file.close()

