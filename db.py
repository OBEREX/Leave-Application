import mysql.connector
from mysql.connector import Error

try:
    # Connect to the MySQL server
    db_connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Balgun996@"
    )

    if db_connection.is_connected():
        db_Info = db_connection.get_server_info()
        print("Connected to MySQL Server version ", db_Info)

except Error as e:
    print("Error while connecting to MySQL", e)

try:   
    # Create a database if it doesn't exist
    db_cursor = db_connection.cursor()
    db_cursor.execute("CREATE DATABASE IF NOT EXISTS leave_request_app")
    db_cursor.close()

    print("Created succesfully")

except Error as e:
    print("Error while creating MySQL database", e)


# Connect to the newly created database
db_connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Balgun996@",
    database="leave_request_app"
)

# Create the Employee Details table
try:
    create_employee_details_table = """
    CREATE TABLE IF NOT EXISTS EmployeeDetails (
        EmployeeId VARCHAR(40) PRIMARY KEY, -- In the format "[team]-[4-digit sequential number]"
        FirstName VARCHAR(50),
        LastName VARCHAR(50),
        Email VARCHAR(100),
        Team VARCHAR(20),
        EmployeeSequentialID INT AUTO_INCREMENT, -- Auto-incremented sequential ID for each employee
        UNIQUE KEY (EmployeeSequentialID)
    );
    """
    create_employee_id_trigger = """
    CREATE TRIGGER set_employee_id_trigger BEFORE INSERT ON EmployeeDetails
    FOR EACH ROW
    BEGIN
        SET NEW.EmployeeId = CONCAT(NEW.Team, '-', LPAD((SELECT COALESCE(MAX(SUBSTRING_INDEX(EmployeeId, '-', -1) + 1), 1) FROM EmployeeDetails WHERE Team = NEW.Team), 4, '0'));
    END;

    """ 

    db_cursor = db_connection.cursor()

    db_cursor.execute(create_employee_details_table)
    db_cursor.execute(create_employee_id_trigger)
except Error as e:
    print("Error while creating employee table", e)

# Create the Leave Request Log table
try:
    create_leave_request_log_table = """
    CREATE TABLE IF NOT EXISTS LeaveRequestLog (
        LeaveId VARCHAR(40) PRIMARY KEY, -- In the format "[leave type]-[4-digit sequential number]"
        EmployeeId VARCHAR(40),
        Year INT,
        TimeLeaveRequestSent TIMESTAMP,
        LeaveStartDate DATE,
        LeaveReturnDate DATE,
        LeaveType VARCHAR(20),
        ReasonForLeave TEXT,
        LeaveSequentialID INT AUTO_INCREMENT, -- Auto-incremented sequential ID for each leave request
        UNIQUE KEY (LeaveSequentialID),
        FOREIGN KEY (EmployeeId) REFERENCES EmployeeDetails(EmployeeId)
    );
    """

    create_leave_id_trigger = """
    CREATE TRIGGER set_leave_id_trigger BEFORE INSERT ON LeaveRequestLog
    FOR EACH ROW
    BEGIN
        SET NEW.LeaveId = CONCAT(NEW.LeaveType, '-', LPAD((SELECT COALESCE(MAX(SUBSTRING_INDEX(LeaveId, '-', -1) + 1), 1) FROM LeaveRequestLog WHERE LeaveType = NEW.LeaveType), 4, '0'));
    END;

    """

    db_cursor.execute(create_leave_request_log_table)
    db_cursor.execute(create_leave_id_trigger)

except Error as e:
    print("Error while creating log table", e)

# Create the Last Requested Leave table
try:
    create_last_requested_leave_table = """
    CREATE TABLE IF NOT EXISTS LastRequestedLeave (
        EmployeeId VARCHAR(10)PRIMARY KEY,
        LeaveId VARCHAR(10),
        Year INT,
        AnnualLeaveLeft INT,
        LeaveTakenInAYear INT,
        FOREIGN KEY (EmployeeId) REFERENCES EmployeeDetails(EmployeeId),
        FOREIGN KEY (LeaveId) REFERENCES LeaveRequestLog(LeaveId)
    )
    """
    db_cursor.execute(create_last_requested_leave_table)
except Error as e:
    print("Error while connecting to MySQL", e)
    
print("Created succesfully")

db_connection.commit()

# Close the database connection
db_cursor.close()
db_connection.close()
