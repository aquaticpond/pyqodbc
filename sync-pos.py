import pypyodbc
import pymysql
import os
from configparser import ConfigParser
from lib.database import Database
from lib.quickbooks.entity import Entity
from lib.quickbooks.pos.inventory import Inventory
from lib.quickbooks.pos.sales_receipt import *

conf = ConfigParser()
conf.read_file(open('config.ini'))

# configuration
mysql_host = conf.get('mysql', 'host')
mysql_port = conf.getint('mysql', 'port')
mysql_user = conf.get('mysql', 'user')
mysql_password = conf.get('mysql', 'password')
mysql_db = conf.get('mysql', 'schema')
qodbc_dsn = conf.get('qodbc', 'dsn')

# set defaults
Entity.company_file = conf.get('company', 'file_number')

if(conf.get('company', 'refresh_from')):
    Entity.last_entry_datetime = conf.get('company', 'refresh_from')


rackspace = Database(pymysql.connect(host=mysql_host, port=mysql_port, user=mysql_user, passwd=mysql_password, db=mysql_db, use_unicode=True, charset="utf8"))
quickbooks = Database(pypyodbc.connect('DSN='+qodbc_dsn, autocommit=True))

print('connected')

SalesReceipt(quickbooks,rackspace).sync()
SalesReceiptItem(quickbooks,rackspace).sync()
Inventory(quickbooks,rackspace).sync()

rackspace.disconnect()
quickbooks.disconnect()

print('disconnected')