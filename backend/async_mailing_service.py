import aiohttp
import asyncio
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage

async def send_async_email(subject, body, requesters_email):
    sender_email = 'ali.balogun@escapetech.net'
    sender_password = 'Balogun996@'
    receiver_email = 'alibalogun996@gmail.com'
    cc_email = 'olaoluwa@escapetech.net'
    smtp_server = 'mail.escapetech.net'
    smtp_port = 465

    # Create the email message
    message = MIMEMultipart()
    message['From'] = sender_email
    message['To'] = receiver_email
    message['Cc'] = cc_email
    message['Bcc'] = requesters_email
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

    # Create the message content as a string
    message_content = message.as_string()

    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(
                f"https://{smtp_server}:{smtp_port}",
                auth=aiohttp.BasicAuth(sender_email, sender_password),
                data=message_content,
                headers={'Content-Type': 'text/plain'}
            ) as response:
                if response.status == 200:
                    print("Email sent successfully")
                else:
                    print("Failed to send email")
        except Exception as e:
            print(f"Error: {e}")

async def main():
    subject = "Test Subject"
    body = "This is a test email."
    recipients = ["recipient@example.com"]
    requesters_email = "yourrequester@example.com"

    await send_async_email(subject, body, requesters_email)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
