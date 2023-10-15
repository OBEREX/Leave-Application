import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage

def send_email(subject, body, requesters_email):
    # Email configuration
    sender_email = 'ali.balogun@escapetech.net'
    sender_password = 'Balogun996@'
    receiver_email = 'alibalogun996@gmail.com'
    cc_email = 'olaoluwa@escapetech.net'
    smtp_server = 'mail.escapetech.net'
    smtp_port = 465  # Use the SMTP Port provided for outgoing emai

    # Create the email message
    message = MIMEMultipart()
    message['From'] = sender_email
    message['To'] = receiver_email
    message['Cc'] = cc_email
    message['Bcc']  = requesters_email
    message['Subject'] = subject

    # Define the email signature text
    signature = """
    Regards,
    
    <img src="cid:signature.png" style="float: left; padding-right: 10px;">
    
    e-Scape Technologies Limited.
    
    Project Action Officer
    
    Abuja: 18 Gaborone Street, Wuse Zone 2. FCT Abuja
    Lagos: 12 Olaribiro Street, off Allen Avenue, Ikeja Lagos.
    
    T: +234 803 550 3375
    Website: https://www.escapetech.net
    """

    # Attach the image
    with open('frontend\Images\signature.png', 'rb') as image_file:
        image = MIMEImage(image_file.read(), name='signature.png')
    message.attach(image)

    # Attach the body
    message.attach(MIMEText(signature, 'html'))
    message.attach(MIMEText(body, 'html'))


    # Connect to the SMTP server
    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()
    server.login(sender_email, sender_password)

    # Send the email
    server.sendmail(sender_email, receiver_email, message.as_string())

    # Close the server
    server.quit()

# Usage