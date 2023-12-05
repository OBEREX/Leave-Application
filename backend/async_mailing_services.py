import asyncio
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage

async def send_email(
    last_name, first_name, email, leave_start_date, leave_end_date, reason_for_leave, leave_type
):
    # Email configuration
    sender_email = 'applicationleave8@gmail.com'
    sender_password = 'dlepqqcaqiauzzjo'  # Replace with your Gmail App Password
    to_email = 'alibalogun996@gmail.com'  # Replace with the recipient's email address
    cc_email = 'chimeremezeanyaibe73@gmail.com'  # Add other recipients if needed
    smtp_server = "smtp.gmail.com"
    smtp_port = 587  # Use the SMTP Port provided for outgoing email

    # Create the email message
    message = MIMEMultipart()
    message['From'] = sender_email
    message['To'] = to_email
    message['Cc'] = cc_email
    message['Bcc'] = email
    message['Subject'] = f"{last_name} {first_name}'s Leave Request Submission"

    # Your HTML template with the <img> tag
    html_template = """
    <p>Good Day,</p>
    <p>I would like to inform you that {first_name} would like to request for a {leave_type} leave</p>
    <p>and would be gone from {leave_start_date} to {leave_end_date} for the reason given as {reason_for_leave}</p>
    <p>Best regards,</p>
    <p>HR Officer</p>
    <p><img src="cid:signature.png" alt="Image Description" width="108" height="60" style="width: 1.125in; height: .625in"></p>
    <p>Abuja: 18 Gaborone Street, Wuse Zone 2. FCT Abuja<br>Lagos: 12 Olaribiro Street, off Allen Avenue, Ikeja Lagos.</p>
    <p>T: +234 803 550 3375<br>Website: <a href="https://www.escapetech.net/" style="color: #0563C1;">https://www.escapetech.net</a></p>
    """

    html_content = html_template.format(
        first_name=first_name,
        leave_type=leave_type,
        leave_start_date=leave_start_date,
        leave_end_date=leave_end_date,
        reason_for_leave=reason_for_leave,
    )

    # Create a MIMEText object with the HTML content
    html_message = MIMEText(html_content, "html")

    # Attach the image with a Content-ID
    with open(r'C:\Users\Dell\Documents\ALi\Dev\Leave Application\frontend\Images\company-logo.png', 'rb') as image_file:
        image = MIMEImage(image_file.read(), name='signature.png')
        image.add_header("Content-ID", "<signature.png>")
        message.attach(image)

    message.attach(html_message)

    # Connect to the SMTP server asynchronously
    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()
    server.login(sender_email, sender_password)

    # Send the email asynchronously
    await server.sendmail(sender_email, to_email, message.as_string())

    # Close the server
    server.quit()

# Example usage within an async function
async def main():
    await send_email("Doe", "John", "johndoe@gmail.com", "2023-10-25", "2023-10-30", "Vacation", "Annual Leave")

# Run the main async function
if __name__ == "__main__":
    asyncio.run(main())
