import mysql.connector

db_conn = mysql.connector.connect(host="localhost", user="root",
password="password", database="events")

db_cursor = db_conn.cursor()

db_cursor.execute('''
        CREATE TABLE blood_pressure
        (id INT NOT NULL AUTO_INCREMENT,
        patient_id VARCHAR(250) NOT NULL,
        device_id VARCHAR(250) NOT NULL,
        systolic INTEGER NOT NULL,
        diastolic INTEGER NOT NULL,
        timestamp VARCHAR(100) NOT NULL,
        trace_id VARCHAR(100) NOT NULL,
        date_created VARCHAR(100) NOT NULL,
        CONSTRAINT blood_pressure_pk PRIMARY KEY (id))
        ''')

db_cursor.execute('''
        CREATE TABLE heart_rate
        (id INT NOT NULL AUTO_INCREMENT,
        patient_id VARCHAR(250) NOT NULL,
        device_id VARCHAR(250) NOT NULL,
        heart_rate INTEGER NOT NULL,
        timestamp VARCHAR(100) NOT NULL,
        trace_id VARCHAR(100) NOT NULL,
        date_created VARCHAR(100) NOT NULL,
        CONSTRAINT heart_rate_pk PRIMARY KEY (id))
        ''')
        
db_conn.commit()
db_conn.close()