from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import mysql.connector
from datetime import datetime
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import os

app = FastAPI()

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

class LastRequestedLeaveModel(BaseModel):
    EmployeeId: str
    LeaveId: str
    Year: int
    AnnualLeaveLeft: int
    LeaveTakenInAYear: int


# Serve the static files from the 'frontend' directory
app.mount("/static", StaticFiles(directory="frontend"), name="static")

# Define a route to serve the HTML form
@app.get("/")
async def read_root():
    html_path = os.path.join("frontend", "index.html")  # Replace with the actual path to your HTML file
    return FileResponse(html_path)

@app.post("/submit_leave_request")
async def submit_leave_request(request: LeaveRequest):
     # Check if a record with the same email already exists
    query = "SELECT EmployeeId FROM EmployeeDetails WHERE Email = %s"
    email_check_values = (request.email,)
    db_cursor.execute(query, email_check_values)
    existing_employee = db_cursor.fetchone()

    print(request.leave_type,request.other_leave_option)

    if existing_employee:
        # A record with the same email exists, use the existing EmployeeId
        employee_id = existing_employee[0]
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
        employee_id = db_cursor.lastrowid
    
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
    else :
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
    return {"message": "Leave request submitted successfully"}

@app.get("/success_page.html", response_class=FileResponse)
async def get_success_page():
    return "static/success_page.html"  # Update with the correct path to your HTML file

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
