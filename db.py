import mysql.connector

# Connect to the MySQL server
db_connection = mysql.connector.connect(
    host="127.0.0.1",
    user="root",
    password="escapetech"
)

# Create a database if it doesn't exist
db_cursor = db_connection.cursor()
db_cursor.execute("CREATE DATABASE IF NOT EXISTS leave_request_app")
db_cursor.close()

# Connect to the newly created database
db_connection = mysql.connector.connect(
    host="your_mysql_host",
    user="your_mysql_username",
    password="your_mysql_password",
    database="leave_request_app"
)

# Create the Employee Details table
create_employee_details_table = """
CREATE TABLE IF NOT EXISTS EmployeeDetails (
    EmployeeId INT AUTO_INCREMENT PRIMARY KEY,
    FirstName VARCHAR(255),
    LastName VARCHAR(255),
    Email VARCHAR(255),
    Team VARCHAR(255)
)
"""
db_cursor = db_connection.cursor()
db_cursor.execute(create_employee_details_table)

# Create the Leave Request Log table
create_leave_request_log_table = """
CREATE TABLE IF NOT EXISTS LeaveRequestLog (
    LeaveId INT AUTO_INCREMENT PRIMARY KEY,
    EmployeeId INT,
    Year INT,
    TimeLeaveRequestSent TIMESTAMP,
    LeaveStartDate DATE,
    LeaveReturnDate DATE,
    LeaveType VARCHAR(255),
    ReasonForLeave TEXT,
    FOREIGN KEY (EmployeeId) REFERENCES EmployeeDetails(EmployeeId)
)
"""
db_cursor.execute(create_leave_request_log_table)

# Create the Last Requested Leave table
create_last_requested_leave_table = """
CREATE TABLE IF NOT EXISTS LastRequestedLeave (
    LeaveId INT AUTO_INCREMENT PRIMARY KEY,
    EmployeeId INT,
    Year INT,
    AnnualLeaveLeft INT,
    LeaveTakenInAYear INT,
    FOREIGN KEY (EmployeeId) REFERENCES EmployeeDetails(EmployeeId)
)
"""
db_cursor.execute(create_last_requested_leave_table)

# Close the database connection
db_cursor.close()
db_connection.close()
