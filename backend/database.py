from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import mysql.connector
from mysql.connector import Error


try: 
    db_connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="")  
    # Create a database if it doesn't exist
    db_cursor = db_connection.cursor()
    db_cursor.execute("CREATE DATABASE IF NOT EXISTS leave_request_app")
    db_cursor.close()

    print("Created succesfully")

except Error as e:
    print("Error while creating MySQL database", e)

URL_DATABASE = 'mysql+pymysql://root:@localhost:3306/leave_request_app'


engine = create_engine(URL_DATABASE)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()




