import smtplib
import logging
import imaplib
import telebot
import email
from email.mime.multipart import MIMEMultipart
from email.header import decode_header
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from dotenv import load_dotenv
from email import encoders
from weasyprint import HTML
import os
from i18n import _

load_dotenv()

EMAIL_ADDRESS = os.getenv('EMAIL_ADDRESS')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
IMAP_ADDRESS = os.getenv('IMAP_ADDRESS')
SMTP_ADDRESS = os.getenv('SMTP_ADDRESS')

def email_main(message: telebot.types.Message, bot: telebot.TeleBot, attachment: bool = 0):
    message_parts = message.text.split(' ') if not attachment else message.caption.split(' ')
    if len(message_parts) < 2 and not attachment:
        emails = emails_list()
        if not emails:
            bot.send_message(message.from_user.id, _('email_no_messages'))
            return

        email_list = ""
        for index, email_item in enumerate(emails):
            email_list += f"{index + 1}. {email_item['From']}:\n{email_item['Subject']}\n{_('email_read_command', index=index)}\n\n"

        bot.send_message(message.from_user.id, f"{_('email_list_title', email=EMAIL_ADDRESS)}\n\n{email_list}", parse_mode='Markdown')
        return
    
    try:
        current_directory = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        template = os.path.join(current_directory, 'data', 'email.html')

        if attachment:
            file_info = bot.get_file(message.document.file_id)
            downloaded_file = bot.download_file(file_info.file_path)

            save_path = os.path.join(current_directory, message.document.file_name)
            os.makedirs(os.path.dirname(save_path), exist_ok=True)

            with open(save_path, 'wb') as new_file:
                new_file.write(downloaded_file)

            send_email(message_parts[1], ' '.join(message_parts[2:]), template, save_path)
            os.remove(save_path)
        else:
            send_email(message_parts[1], ' '.join(message_parts[2:]), template)
        
        bot.send_message(message.from_user.id, _('email_sent_success'))
    except Exception as e:
        logging.error(f'Error in email: {e}')
        bot.send_message(message.from_user.id, _('email_error'))

def send_email(to_address: str, subject: str, template_path: str, attachment_path: str = ""):
    try:
        with open(template_path, 'r', encoding='utf-8') as file:
            email_content = file.read()

        email_content = email_content.replace('{{message}}', subject)

        msg = MIMEMultipart()
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = to_address
        
        from config import NAME
        msg['Subject'] = _('email_subject_default', name=NAME)

        msg.attach(MIMEText(email_content, 'html'))

        if len(attachment_path) > 0:
            with open(attachment_path, 'rb') as attachment:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.read())
                encoders.encode_base64(part)
                part.add_header(
                    'Content-Disposition',
                    f'attachment; filename="{os.path.basename(attachment_path)}"',
                )
                msg.attach(part)

        with smtplib.SMTP_SSL(SMTP_ADDRESS, 465) as server:
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(msg)

        logging.info('Email sent successfully')
    except Exception as e:
        logging.error(f'Email failed to send: {e}')
        raise Exception(_('email_send_failed'))

def emails_list():
    emails = []
    try:
        mail = imaplib.IMAP4_SSL(IMAP_ADDRESS)
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

def email_read_body(num: int):
    try:
        mail = imaplib.IMAP4_SSL(IMAP_ADDRESS)
        mail.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        mail.select('inbox')

        _, messages = mail.search(None, 'ALL')
        email_ids = messages[0].split()

        email_id = email_ids[num]

        total_emails = len(email_ids)
        if total_emails > 10:
            email_id = email_ids[-10 + num]
        else:
            email_id = email_ids[num]

        _, msg_data = mail.fetch(email_id, '(RFC822)')
        for response_part in msg_data:
            if isinstance(response_part, tuple):
                msg = email.message_from_bytes(response_part[1])
                subject, encoding = decode_header(msg['Subject'])[0]
                if isinstance(subject, bytes):
                    subject = subject.decode(encoding if encoding else 'utf-8')
                from_ = msg.get('From')
                body = ''

                if msg.is_multipart():
                    for part in msg.walk():
                        part.get_content_type()
                        content_disposition = str(part.get('Content-Disposition'))

                        if 'attachment' not in content_disposition:
                            payload = part.get_payload(decode=True)
                            if payload:
                                body += payload.decode(part.get_content_charset() or 'utf-8')
                else:
                    payload = msg.get_payload(decode=True)
                    if payload:
                        body = payload.decode(msg.get_content_charset() or 'utf-8')

                mail.logout()
                return {
                    'From': from_,
                    'Subject': subject,
                    'Body': body
                }
    except Exception as e:
        logging.error(f'Error in email_read: {e}')
        raise Exception('Error in email_read')

def email_read(message: telebot.types.Message, bot: telebot.TeleBot):
    try:
        email_index = int(message.text.split('_')[-1])
        
        email = email_read_body(email_index)
        email_html = f"<h1>{email['From']}</h1><h2>{email['Subject']}</h2><p>{email['Body']}</p>"
        
        pdf_path = f"/tmp/email_{email_index}.pdf"
        HTML(string=email_html).write_pdf(pdf_path)
        
        with open(pdf_path, 'rb') as pdf_file:
            bot.send_document(message.from_user.id, pdf_file)
        
        os.remove(pdf_path)
    except Exception as e:
        logging.error(f"Error handling email_read command: {e}")
        bot.send_message(message.from_user.id, _('email_read_error'))