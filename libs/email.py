import smtplib
import logging
import imaplib
import email
from email.mime.multipart import MIMEMultipart
from email.header import decode_header
from email.mime.text import MIMEText
from dotenv import load_dotenv
import os

load_dotenv()

# TODO: прикрепление файлов к сообщению

EMAIL_ADDRESS = os.getenv('EMAIL_ADDRESS')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')

def send_email(to_address, subject, template_path):
    try:
        with open(template_path, 'r', encoding='utf-8') as file:
            email_content = file.read()

        email_content = email_content.replace('{{message}}', ' '.join(subject))

        msg = MIMEMultipart()
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = to_address
        msg['Subject'] = "Сообщение от Иванущенко Виталия"

        msg.attach(MIMEText(email_content, 'html'))

        with smtplib.SMTP_SSL('smtp.beget.com', 465) as server:
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(msg)

        logging.info('Email sent successfully')
    except Exception as e:
        logging.error(f'Email failed to send: {e}')
        raise Exception('Email failed to send')

def emails_list():
    emails = []
    try:
        mail = imaplib.IMAP4_SSL('imap.beget.com')
        mail.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        mail.select('inbox')

        _, messages = mail.search(None, 'ALL')
        email_ids = messages[0].split()

        last_10_email_ids = email_ids[-10:]

        for email_id in last_10_email_ids:
            _, msg_data = mail.fetch(email_id, '(RFC822)')
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])
                    subject, encoding = decode_header(msg['Subject'])[0]
                    if isinstance(subject, bytes):
                        subject = subject.decode(encoding if encoding else 'utf-8')
                    from_ = msg.get('From')

                    emails.append({
                        'From': from_,
                        'Subject': subject
                    })

        mail.logout()
    except Exception as e:
        logging.error(f'Error in emails_list: {e}')
    
    return emails