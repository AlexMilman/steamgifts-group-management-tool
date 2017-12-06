# MySql connector of SGMT
# Copyright (C) 2017  Alex Milman

import pymysql
import ConfigParser

config = ConfigParser.ConfigParser()
config.read('../application.config')
host = config.get('MySql', 'Host')
port = int(config.get('MySql', 'Port'))
user = config.get('MySql', 'User')
password = config.get('MySql', 'Password')
db_schema = config.get('MySql', 'DBSchema')


conn = pymysql.connect(host=host, port=port, user=user, passwd=password, db=db_schema)
cur = conn.cursor()
cur.execute("SELECT * FROM GroupGiveaways")

print cur.description

for row in cur:
    print row

cur.close()
conn.close()