from sqlalchemy import Boolean, ForeignKey, Column, Integer, String, DateTime, Date
from sqlalchemy.orm import relationship
from database import Base

from sqlalchemy import event


# Define the EmployeeDetails table
class EmployeeDetails(Base):
    __tablename__ = 'EmployeeDetails'

    EmployeeId = Column(String(40), primary_key=True)
    FirstName = Column(String(50))
    LastName = Column(String(50))
    Email = Column(String(100))
    Team = Column(String(20))
    EmployeeSequentialID = Column(Integer, unique=True, index=True, autoincrement=True)

    # Define a one-to-many relationship with LeaveRequestLog
    leave_requests = relationship('LeaveRequestLog', back_populates='employee_details')

    # Define an event listener for "before_insert" on EmployeeDetails
@event.listens_for(EmployeeDetails, "before_insert")
def set_employee_id(mapper, connection, target):
    # Calculate the EmployeeId based on your logic
    query = """
    SELECT COALESCE(MAX(SUBSTRING_INDEX(EmployeeId, '-', -1) + 1), 1) 
    FROM EmployeeDetails WHERE Team = :team
    """
    max_employee_id = connection.scalar(query, team=target.Team)
    new_employee_id = f"{target.Team}-{max_employee_id:04d}"
    target.EmployeeId = new_employee_id

# Define the LeaveRequestLog table
class LeaveRequestLog(Base):
    __tablename__ = 'LeaveRequestLog'

    LeaveId = Column(String(40), primary_key=True)
    EmployeeId = Column(String(40), ForeignKey('EmployeeDetails.EmployeeId'))
    Year = Column(Integer)
    TimeLeaveRequestSent = Column(DateTime)
    LeaveStartDate = Column(Date)
    LeaveReturnDate = Column(Date)
    LeaveType = Column(String(20))
    ReasonForLeave = Column(String)
    LeaveSequentialID = Column(Integer, unique=True, index=True, autoincrement=True)

    # Define a many-to-one relationship with EmployeeDetails
    employee_details = relationship('EmployeeDetails', back_populates='leave_requests')

class Employee(Base):
    __tablename__ = 'employeeDetails'

    id = Column(Integer, primary_key=True, index=True)
    employeeName = Column(String(50), unique=True)
    employeeEmail = Column(String(50), unique=True)
    employeeTeam = Column(String(20))

class Log(Base):
    __tablename__ = 'leaveRequestLog'

    id = Column(Integer, primary_key=True, index=True)
    EmployeeId = Column(Integer, ForeignKey("employeeDetails.id"))
    year =  Column(Integer)
    timeLeaveRequestSent = Column(TIMESTAMP)
    LeaveStartDate = Column(DATE)
    LeaveReturnDate = Column(DATE)
    leaveType = Column(String(20))
    reasonForLeave  = Column(String(100))

class LastRequest(Base):
    __tablename__ = 'LastRequestedLeave'

    employeeId = Column(Integer, ForeignKey("employeeDetails.id"), primary_key=True, index=True)
    year =  Column(Integer)
    annualLeaveLeft = Column(Integer)
    leaveTakenInTheYear = Column(Integer)
    lastLeaveTaken = Column(Integer, ForeignKey("leaveRequestLog.id"))