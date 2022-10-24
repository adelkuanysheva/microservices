import mysql.connector

db_conn = mysql.connector.connect(host="localhost", user="root",
password="delta123", database="ride_heartrate")

db_cursor = db_conn.cursor()
db_cursor.execute('''
DROP TABLE ride, heart_rate
''')
db_conn.commit()
db_conn.close()