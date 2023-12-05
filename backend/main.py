from fastapi import FastAPI,  Request
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles


import os
## import models
from pydantic import BaseModel
import mysql.connector
from datetime import datetime, date
from fastapi.templating import Jinja2Templates
import asyncio
from mailing_services import send_email


# Define the path to your HTML templates relative to the current script
templates = Jinja2Templates(directory="frontend\dashboard")



app = FastAPI()


# Replace these with your database credentials
db_config = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "database": "leave_request_app",
}
with open(r"C:\Users\Dell\Desktop\credentials\mysql_credentials.txt","r") as f:
        db_config["password"] = f.readline()

# Create a MySQL connection
db_connection = mysql.connector.connect(**db_config)
db_cursor = db_connection.cursor()


class LeaveRequest(BaseModel):
    first_name: str
    last_name: str
    email: str
    team: str
    leave_start_date: str
    leave_end_date: str
    leave_type: str
    other_leave_option: str
    reason_for_leave: str

class StatusRequest(BaseModel):
    id: str
    first_name: str
    last_name: str
    leave_type: str
    leave_start_date: date
    leave_end_date: date
    reason_for_leave: str
    status: str  # 'pending', 'approved', or 'rejected'


# Serve the static files from the 'frontend' directory
app.mount("/static", StaticFiles(directory="frontend"), name="static")

# Define a route to serve the HTML form
@app.get("/")
def read_root():
    html_path = os.path.join("frontend", "welcome_page.html")  # Replace with the actual path to your HTML file
    return FileResponse(html_path)

@app.get("/admin_login_page")
def get_admin_login_page():
    html_path = os.path.join("frontend", "admin_login.html")  # Replace with the actual path to your HTML file
    return FileResponse(html_path)

@app.get("/form_page")
def get_form_page():
    html_path = os.path.join("frontend", "index.html")  # Update with the correct path to your HTML file
    return FileResponse(html_path)

# Function to check if an employee with the given email exists and return the employee ID
def get_or_create_employee(request: LeaveRequest):
    # Check if an employee with the given email and team already exists
    query = "SELECT EmployeeId FROM EmployeeDetails WHERE Email = %s AND Team = %s"
    query_values = (request.email, request.team)
    db_cursor.execute(query, query_values)
    existing_employee = db_cursor.fetchone()

    if existing_employee:
        # A record with the same email exists, use the existing EmployeeId
        print(existing_employee[0])
        return existing_employee[0]
    else:
        # Insert a new record if no existing record found
        insert_query = """
        INSERT INTO EmployeeDetails (FirstName, LastName, Email, Team)
        VALUES (%s, %s, %s, %s)
        """
        insert_values = (request.first_name, request.last_name, request.email, request.team)

        db_cursor.execute(insert_query, insert_values)
        db_connection.commit()

        # Get the EmployeeId of the newly inserted record
         # Query for the newly inserted employee's ID
        query = "SELECT EmployeeId FROM EmployeeDetails WHERE Email = %s AND Team = %s"
        db_cursor.execute(query, query_values)
        new_employee = db_cursor.fetchone()
        if new_employee:
            employee_id = new_employee[0]
        print(employee_id)
        return employee_id

# Function to insert a leave request into the database
def insert_leave_request(employee_id, request: LeaveRequest):
    query = """
    INSERT INTO LeaveRequestLog (EmployeeId, Year, TimeLeaveRequestSent, LeaveStartDate, LeaveReturnDate, LeaveType, ReasonForLeave)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    if request.leave_type == "Others":
        values = (
            employee_id,
            datetime.now().year,
            datetime.now(),
            request.leave_start_date,
            request.leave_end_date,
            request.other_leave_option,
            request.reason_for_leave,
        )
    else:
        values = (
            employee_id,
            datetime.now().year,
            datetime.now(),
            request.leave_start_date,
            request.leave_end_date,
            request.leave_type,
            request.reason_for_leave,
        )
    db_cursor.execute(query, values)
    db_connection.commit()

# Your route for leave submission
@app.post("/submit_leave_request")
async def submit_leave_request(request: LeaveRequest):
    # Get or create employee
    employee_id = get_or_create_employee(request)
    print(employee_id)
    # Insert leave request
    insert_leave_request(employee_id, request)
    # sending email
    try:
        send_email(
            last_name=request.last_name,
            first_name=request.first_name,
            email=request.email,
            leave_start_date=request.leave_start_date,
            leave_end_date=request.leave_end_date,
            reason_for_leave=request.reason_for_leave,
            leave_type=request.leave_type,
        )
    except:
        pass
   
    print("Successful")
    # Redirect to the success page
    return {'url': '/success_page'}

@app.get("/fetch-pending-requests" , response_class=HTMLResponse)
async def fetch_pending_requests(request: Request):
    query = '''
    SELECT 
        LeaveRequestLog.LeaveId,
        EmployeeDetails.FirstName, 
        EmployeeDetails.LastName,  
        LeaveRequestLog.LeaveType,
        LeaveRequestLog.LeaveStartDate,
        LeaveRequestLog.LeaveReturnDate,
        LeaveRequestLog.ReasonForLeave,
        LeaveRequestLog.LeaveStatus
    FROM
        EmployeeDetails
    INNER JOIN LeaveRequestLog ON EmployeeDetails.EmployeeId = LeaveRequestLog.EmployeeId
    WHERE LeaveStatus = 'pending'
    '''
    db_cursor.execute(query)
    results = db_cursor.fetchall()
    column_names = ("id", "first_name", "last_name", "leave_type", "leave_start_date", "leave_end_date", "reason_for_leave", "status")
    pending_requests = [StatusRequest(**dict(zip(column_names, row))) for row in results]
    #return pending_requests
    return templates.TemplateResponse("index.html", {"request": request, "pending_requests": pending_requests})


@app.get("/fetch-ongoing-requests" , response_class=HTMLResponse)
async def fetch_ongoing_requests(request: Request):
    query = '''
    SELECT 
            LeaveRequestLog.LeaveId,
            EmployeeDetails.FirstName, 
            EmployeeDetails.LastName,  
            LeaveRequestLog.LeaveType,
            LeaveRequestLog.LeaveStartDate,
            LeaveRequestLog.LeaveReturnDate,
            LeaveRequestLog.ReasonForLeave,
            LeaveRequestLog.LeaveStatus
        FROM
            EmployeeDetails
        INNER JOIN LeaveRequestLog
        ON EmployeeDetails.EmployeeId = LeaveRequestLog.EmployeeId
        WHERE 
            LeaveStatus = 'approved' AND 
            LeaveStartDate < CURDATE() AND 
            LeaveReturnDate > CURDATE()
    '''
    db_cursor.execute(query)
    results = db_cursor.fetchall()
    column_names = ("id", "first_name", "last_name", "leave_type", "leave_start_date", "leave_end_date", "reason_for_leave", "status")
    ongoing_requests = [StatusRequest(**dict(zip(column_names, row))) for row in results]

    return templates.TemplateResponse("ongoing.html", {"request": request, "ongoing_requests": ongoing_requests})

@app.get("/fetch-not_started-requests" , response_class=HTMLResponse)
async def fetch_ongoing_requests(request: Request):
    query = '''
    SELECT 
        LeaveRequestLog.LeaveId,
        EmployeeDetails.FirstName, 
        EmployeeDetails.LastName,  
        LeaveRequestLog.LeaveType,
        LeaveRequestLog.LeaveStartDate,
        LeaveRequestLog.LeaveReturnDate,
        LeaveRequestLog.ReasonForLeave,
        LeaveRequestLog.LeaveStatus
    FROM
        EmployeeDetails
    INNER JOIN LeaveRequestLog ON EmployeeDetails.EmployeeId = LeaveRequestLog.EmployeeId
    WHERE LeaveStatus = 'approved' 
    AND LeaveStartDate > CURDATE()
    AND LeaveReturnDate > CURDATE()
    '''
    db_cursor.execute(query)
    results = db_cursor.fetchall()
    column_names = ("id", "first_name", "last_name", "leave_type", "leave_start_date", "leave_end_date", "reason_for_leave", "status")
    not_started_requests = [StatusRequest(**dict(zip(column_names, row))) for row in results]

    return templates.TemplateResponse("not_started.html", {"request": request, "not_started_requests": not_started_requests})

@app.get("/fetch-all-requests" , response_class=HTMLResponse)
async def fetch_ongoing_requests(request: Request):
    query = '''
    SELECT 
        LeaveRequestLog.LeaveId,
        EmployeeDetails.FirstName, 
        EmployeeDetails.LastName,  
        LeaveRequestLog.LeaveType,
        LeaveRequestLog.LeaveStartDate,
        LeaveRequestLog.LeaveReturnDate,
        LeaveRequestLog.ReasonForLeave,
        LeaveRequestLog.LeaveStatus
    FROM
        EmployeeDetails
    INNER JOIN LeaveRequestLog ON EmployeeDetails.EmployeeId = LeaveRequestLog.EmployeeId
    '''
    db_cursor.execute(query)
    results = db_cursor.fetchall()
    column_names = ("id", "first_name", "last_name", "leave_type", "leave_start_date", "leave_end_date", "reason_for_leave", "status")
    all_requests = [StatusRequest(**dict(zip(column_names, row))) for row in results]

    return templates.TemplateResponse("all_request.html", {"request": request, "all_requests": all_requests})



@app.get("/accept_leave/{request_id}")
def accept_leave(request: Request, request_id):
    query = "UPDATE LeaveRequestLog SET LeaveStatus = 'approved' WHERE LeaveId = %s"
    values = (request_id,)
    db_cursor.execute(query, values)
    db_connection.commit()
    return RedirectResponse("/fetch-pending-requests")

@app.get("/reject_leave/{request_id}")
def reject_leave(request: Request, request_id):
    query = "UPDATE LeaveRequestLog SET LeaveStatus = 'rejected' WHERE LeaveId = %s"
    values = (request_id,)
    db_cursor.execute(query, values)
    db_connection.commit()
    return RedirectResponse("/fetch-pending-requests")




@app.get("/success_page")
def get_success_page():
    html_path = os.path.join("frontend", "success_page.html")  # Update with the correct path to your HTML file
    return FileResponse(html_path)








if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)

