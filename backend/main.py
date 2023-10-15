from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
import os
## import models
from pydantic import BaseModel
import mysql.connector
from datetime import datetime
from async_mailing_service import send_async_email 
app = FastAPI()
## models.Base.metadata.create_all(bind=engine)

# Replace these with your database credentials
db_config = {
    "host": "localhost",
    "user": "root",
    "password": "Balgun996@",
    "database": "leave_request_app",
}

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

# Serve the static files from the 'frontend' directory
app.mount("/static", StaticFiles(directory="frontend"), name="static")

# Define a route to serve the HTML form
@app.get("/")
def read_root():
    html_path = os.path.join("frontend", "index.html")  # Replace with the actual path to your HTML file
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
    if request.leave_type == "others":
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
    subject = f"{request.last_name} {request.first_name}'s Leave Request Submission"
    body = f'''
        Good Day,
        I would like to inform you that {request.first_name} would like to request for a {request.leave_type} leave 
        and would be gone from {request.leave_start_date} to {request.leave_end_date} for the reason given as
        {request.reason_for_leave}
    '''
    await send_async_email(subject=subject,body=body,requesters_email=request.email)
    print("sucesssfull")
    # Redirect to the success page
    return {'url': '/success_page'}


@app.get("/success_page")
def get_success_page():
    html_path = os.path.join("frontend", "success_page.html")  # Update with the correct path to your HTML file
    return FileResponse(html_path)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)

