import smtplib
import logging
import imaplib
import telebot
import socket
import email
import time
import ssl
import sys
import os
from email.mime.multipart import MIMEMultipart
from email.header import decode_header
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from dotenv import load_dotenv
from weasyprint import HTML
from email import encoders
from telebot import types
from i18n import _

load_dotenv()

EMAIL_ADDRESS = os.getenv('EMAIL_ADDRESS')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
IMAP_ADDRESS = os.getenv('IMAP_ADDRESS')
SMTP_ADDRESS = os.getenv('SMTP_ADDRESS')

email_states = {}

class EmailStates:
    IDLE = 0
    WAITING_FOR_RECIPIENT = 1
    WAITING_FOR_SUBJECT = 2
    WAITING_FOR_BODY = 3
    WAITING_FOR_CONFIRMATION = 4
    WAITING_FOR_ATTACHMENTS = 5

class EmailData:
    def __init__(self, email_idx=None):
        self.email_idx = email_idx
        self.recipient = None
        self.subject = None
        self.body = None
        self.attachments = []
        self.message_id = None

def start_email_send(call, bot, email_idx):
    user_id = call.from_user.id
    
    email_states[user_id] = {
        'state': EmailStates.WAITING_FOR_RECIPIENT,
        'data': EmailData(email_idx)
    }
    
    msg = bot.send_message(
        call.message.chat.id,
        _("email_enter_recipient")
    )
    
    email_states[user_id]['message_id'] = msg.message_id

def handle_email_recipient(message, bot):
    user_id = message.from_user.id
    
    if user_id in email_states and email_states[user_id]['state'] == EmailStates.WAITING_FOR_RECIPIENT:
        email_states[user_id]['data'].recipient = message.text.strip()
        email_states[user_id]['state'] = EmailStates.WAITING_FOR_SUBJECT
        
        if 'message_id' in email_states[user_id]:
            try:
                bot.delete_message(message.chat.id, email_states[user_id]['message_id'])
            except Exception as e:
                logging.error(f"Error deleting message: {e}")
        
        msg = bot.send_message(
            message.chat.id,
            _("email_enter_subject")
        )
        
        email_states[user_id]['message_id'] = msg.message_id

def handle_email_subject(message, bot):
    user_id = message.from_user.id
    
    if user_id in email_states and email_states[user_id]['state'] == EmailStates.WAITING_FOR_SUBJECT:
        email_states[user_id]['data'].subject = message.text.strip()
        email_states[user_id]['state'] = EmailStates.WAITING_FOR_BODY
        
        if 'message_id' in email_states[user_id]:
            try:
                bot.delete_message(message.chat.id, email_states[user_id]['message_id'])
            except Exception as e:
                logging.error(f"Error deleting message: {e}")
        
        msg = bot.send_message(
            message.chat.id,
            _("email_enter_body")
        )
        
        email_states[user_id]['message_id'] = msg.message_id

def handle_email_body(message, bot):
    user_id = message.from_user.id
    
    if user_id in email_states and email_states[user_id]['state'] == EmailStates.WAITING_FOR_BODY:
        email_states[user_id]['data'].body = message.text
        email_states[user_id]['state'] = EmailStates.WAITING_FOR_CONFIRMATION
        
        if 'message_id' in email_states[user_id]:
            try:
                bot.delete_message(message.chat.id, email_states[user_id]['message_id'])
            except Exception as e:
                logging.error(f"Error deleting message: {e}")
        
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(
            types.InlineKeyboardButton(_("email_confirm_send"), callback_data="email_confirm_send"),
            types.InlineKeyboardButton(_("email_cancel"), callback_data="email_cancel")
        )
        markup.add(types.InlineKeyboardButton(_("email_attach_files"), callback_data="email_attach_files"))
        
        email_idx = email_states[user_id]['data'].email_idx
        
        import os
        email_address = os.getenv('EMAIL_ADDRESS')
        if email_idx is not None and ',' in email_address:
            email_list = [email.strip() for email in email_address.split(',')]
            if 0 <= email_idx < len(email_list):
                sender_email = email_list[email_idx]
            else:
                sender_email = email_list[0]
        else:
            sender_email = email_address.split(',')[0].strip()
        
        preview_text = (
            f"*{_('email_preview')}*\n\n"
            f"{_('email_from')}: `{sender_email}`\n"
            f"{_('email_to')}: `{email_states[user_id]['data'].recipient}`\n"
            f"{_('email_subject')}: `{email_states[user_id]['data'].subject}`\n\n"
            f"{_('email_body')}:\n{email_states[user_id]['data'].body}\n\n"
            f"{_('email_confirm_prompt')}"
        )
        
        msg = bot.send_message(
            message.chat.id,
            preview_text,
            parse_mode='Markdown',
            reply_markup=markup
        )
        
        email_states[user_id]['message_id'] = msg.message_id

def handle_email_confirm_send(call, bot):
    user_id = call.from_user.id
    
    if user_id in email_states and email_states[user_id]['state'] == EmailStates.WAITING_FOR_CONFIRMATION:
        try:
            bot.answer_callback_query(call.id)
        except Exception as cb_error:
            logging.error(f"Error answering callback query: {cb_error}")
        
        try:
            email_data = email_states[user_id]['data']
            status_msg = bot.send_message(
                call.message.chat.id,
                _("email_sending"),
                parse_mode='Markdown'
            )
            
            send_email_with_attachments(
                email_data.recipient,
                email_data.subject,
                email_data.body,
                email_data.attachments,
                email_data.email_idx
            )
            
            del email_states[user_id]
            
            try:
                bot.edit_message_text(
                    _("email_sent_success"),
                    call.message.chat.id,
                    call.message.message_id,
                    parse_mode='Markdown'
                )
                bot.delete_message(call.message.chat.id, status_msg.message_id)
            except Exception as e:
                logging.error(f"Error updating message after email sent: {e}")
                try:
                    bot.edit_message_text(
                        _("email_sent_success"),
                        call.message.chat.id,
                        status_msg.message_id,
                        parse_mode='Markdown'
                    )
                except:
                    pass
                
        except Exception as e:
            logging.error(f"Error sending email: {e}")
            try:
                bot.send_message(call.message.chat.id, _("email_send_error_details").format(error=e))
            except Exception as msg_error:
                logging.error(f"Error sending error message: {msg_error}")

def handle_email_cancel(call, bot):
    user_id = call.from_user.id
    
    if user_id in email_states:
        del email_states[user_id]
        
        try:
            bot.edit_message_text(
                _("email_cancelled"),
                call.message.chat.id,
                call.message.message_id,
                parse_mode='Markdown'
            )
            bot.answer_callback_query(call.id)
        except Exception as e:
            logging.error(f"Error updating message after cancel: {e}")
            try:
                bot.send_message(
                    call.message.chat.id,
                    _("email_cancelled"),
                    parse_mode='Markdown'
                )
            except:
                pass

def handle_email_attach_files(call, bot):
    user_id = call.from_user.id
    
    if user_id in email_states and email_states[user_id]['state'] == EmailStates.WAITING_FOR_CONFIRMATION:
        email_states[user_id]['state'] = EmailStates.WAITING_FOR_ATTACHMENTS
        
        try:
            bot.edit_message_text(
                _("email_attach_prompt"),
                call.message.chat.id,
                call.message.message_id,
                parse_mode='Markdown'
            )
            bot.answer_callback_query(call.id)
        except Exception as e:
            logging.error(f"Error updating message for attachments: {e}")
            try:
                bot.send_message(
                    call.message.chat.id,
                    _("email_attach_prompt"),
                    parse_mode='Markdown'
                )
            except:
                pass

def handle_email_attachments(message, bot):
    user_id = message.from_user.id
    
    if user_id in email_states and email_states[user_id]['state'] == EmailStates.WAITING_FOR_ATTACHMENTS:
        if message.document:
            file_info = bot.get_file(message.document.file_id)
            file_path = f"temp/{message.document.file_name}"
            
            import os
            os.makedirs("temp", exist_ok=True)
            
            downloaded_file = bot.download_file(file_info.file_path)
            
            with open(file_path, 'wb') as new_file:
                new_file.write(downloaded_file)
                
            email_states[user_id]['data'].attachments.append({
                'path': file_path,
                'name': message.document.file_name
            })
            
            email_states[user_id]['state'] = EmailStates.WAITING_FOR_CONFIRMATION
            
            markup = types.InlineKeyboardMarkup(row_width=2)
            markup.add(
                types.InlineKeyboardButton(_("email_confirm_send"), callback_data="email_confirm_send"),
                types.InlineKeyboardButton(_("email_cancel"), callback_data="email_cancel")
            )
            markup.add(types.InlineKeyboardButton(_("email_attach_more"), callback_data="email_attach_more"))
            
            email_idx = email_states[user_id]['data'].email_idx
            import os
            email_address = os.getenv('EMAIL_ADDRESS')
            if email_idx is not None and ',' in email_address:
                email_list = [email.strip() for email in email_address.split(',')]
                sender_email = email_list[email_idx] if 0 <= email_idx < len(email_list) else email_list[0]
            else:
                sender_email = email_address.split(',')[0].strip()
            
            attachments_info = "\n".join([f"- {att['name']}" for att in email_states[user_id]['data'].attachments])
            
            preview_text = (
                f"*{_('email_preview')}*\n\n"
                f"{_('email_from')}: `{sender_email}`\n"
                f"{_('email_to')}: `{email_states[user_id]['data'].recipient}`\n"
                f"{_('email_subject')}: `{email_states[user_id]['data'].subject}`\n\n"
                f"{_('email_body')}:\n{email_states[user_id]['data'].body}\n\n"
                f"{_('email_attachments')}:\n{attachments_info}\n\n"
                f"{_('email_confirm_prompt')}"
            )
            
            bot.send_message(
                message.chat.id,
                preview_text,
                parse_mode='Markdown',
                reply_markup=markup
            )

def get_email_credentials(email_index=None):
    try:
        if not EMAIL_ADDRESS:
            logging.error("EMAIL_ADDRESS environment variable is not set")
            raise ValueError("Email address is not configured")
            
        if not EMAIL_PASSWORD:
            logging.error("EMAIL_PASSWORD environment variable is not set")
            raise ValueError("Email password is not configured")
            
        if not IMAP_ADDRESS:
            logging.error("IMAP_ADDRESS environment variable is not set")
            raise ValueError("IMAP server is not configured")
            
        if not SMTP_ADDRESS:
            logging.error("SMTP_ADDRESS environment variable is not set")
            raise ValueError("SMTP server is not configured")
            
        if email_index is not None and ',' in EMAIL_ADDRESS:
            email_addresses = [e.strip() for e in EMAIL_ADDRESS.split(',')]
            
            if EMAIL_PASSWORD and ',' in EMAIL_PASSWORD:
                email_passwords = [p.strip() for p in EMAIL_PASSWORD.split(',')]
                if len(email_passwords) < len(email_addresses):
                    email_passwords.extend([email_passwords[-1]] * (len(email_addresses) - len(email_passwords)))
            else:
                email_passwords = [EMAIL_PASSWORD] * len(email_addresses)
                
            if IMAP_ADDRESS and ',' in IMAP_ADDRESS:
                imap_addresses = [i.strip() for i in IMAP_ADDRESS.split(',')]
                logging.info(f"IMAP servers: {imap_addresses}")
                if len(imap_addresses) < len(email_addresses):
                    imap_addresses.extend([imap_addresses[-1]] * (len(email_addresses) - len(imap_addresses)))
            else:
                imap_addresses = [IMAP_ADDRESS.strip()] * len(email_addresses)
                
            if SMTP_ADDRESS and ',' in SMTP_ADDRESS:
                smtp_addresses = [s.strip() for s in SMTP_ADDRESS.split(',')]
                logging.info(f"SMTP servers: {smtp_addresses}")
                if len(smtp_addresses) < len(email_addresses):
                    smtp_addresses.extend([smtp_addresses[-1]] * (len(email_addresses) - len(smtp_addresses)))
            else:
                smtp_addresses = [SMTP_ADDRESS.strip()] * len(email_addresses)
            
            if 0 <= email_index < len(email_addresses):
                selected_email = email_addresses[email_index]
                selected_imap = imap_addresses[email_index].split(',')[0].strip()
                selected_smtp = smtp_addresses[email_index].split(',')[0].strip()
                
                logging.info(f"Using email config {email_index}: EMAIL={selected_email}, IMAP={selected_imap}, SMTP={selected_smtp}")
                
                return {
                    'email': selected_email,
                    'password': email_passwords[email_index],
                    'imap': selected_imap,
                    'smtp': selected_smtp
                }
            else:
                logging.warning(f"Email index {email_index} is out of range, using first email")
                first_imap = imap_addresses[0].split(',')[0].strip()
                first_smtp = smtp_addresses[0].split(',')[0].strip()
                
                return {
                    'email': email_addresses[0],
                    'password': email_passwords[0],
                    'imap': first_imap,
                    'smtp': first_smtp
                }
        else:
            email_addr = EMAIL_ADDRESS.split(',')[0].strip() if EMAIL_ADDRESS else ''
            imap_addr = IMAP_ADDRESS.split(',')[0].strip() if IMAP_ADDRESS else ''
            smtp_addr = SMTP_ADDRESS.split(',')[0].strip() if SMTP_ADDRESS else ''
                
            logging.info(f"Using single email config: EMAIL={email_addr}, IMAP={imap_addr}, SMTP={smtp_addr}")
            
            return {
                'email': email_addr,
                'password': EMAIL_PASSWORD.split(',')[0].strip() if EMAIL_PASSWORD else '',
                'imap': imap_addr,
                'smtp': smtp_addr
            }
    except Exception as e:
        logging.error(f"Error in get_email_credentials: {e}")
        raise ValueError(f"Failed to get email credentials: {str(e)}")

def get_email_list():
    if EMAIL_ADDRESS and ',' in EMAIL_ADDRESS:
        return [email.strip() for email in EMAIL_ADDRESS.split(',')]
    elif EMAIL_ADDRESS:
        return [EMAIL_ADDRESS]
    else:
        logging.error("EMAIL_ADDRESS environment variable is not set")
        return []

def send_email_with_attachments(to_address: str, subject: str, body: str, attachments: list = None, email_index=None):
    try:
        credentials = get_email_credentials(email_index)
        
        current_directory = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        template_path = os.path.join(current_directory, 'data', 'email.html')
        
        if not os.path.exists(template_path):
            logging.error(f"Email template not found at {template_path}")
            raise Exception("Email template not found")
        
        with open(template_path, 'r', encoding='utf-8') as file:
            email_content = file.read()

        email_content = email_content.replace('{{message}}', body)
        
        msg = MIMEMultipart()
        msg['From'] = credentials['email']
        msg['To'] = to_address
        msg['Subject'] = subject
        
        msg.attach(MIMEText(email_content, 'html'))
        
        if attachments:
            for attachment in attachments:
                try:
                    with open(attachment['path'], 'rb') as file:
                        part = MIMEBase('application', 'octet-stream')
                        part.set_payload(file.read())
                        encoders.encode_base64(part)
                        part.add_header(
                            'Content-Disposition',
                            f'attachment; filename="{attachment["name"]}"'
                        )
                        msg.attach(part)
                    
                    try:
                        os.remove(attachment['path'])
                    except:
                        pass
                except Exception as attach_err:
                    logging.error(f"Error with attachment {attachment['name']}: {attach_err}")
        
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        
        smtp_server = credentials['smtp']
        logging.info(f"Connecting to SMTP server {smtp_server} as {credentials['email']} with Python {sys.version}")
        logging.info(f"SSL info: OpenSSL version: {ssl.OPENSSL_VERSION}")
        
        try:
            logging.info(f"Attempting SSL connection to {smtp_server}:465")
            with smtplib.SMTP_SSL(smtp_server, 465, timeout=15, context=context) as server:
                server.login(credentials['email'], credentials['password'])
                server.send_message(msg)
                logging.info('Email sent successfully via SMTP_SSL')
                return True
        except (socket.timeout, ssl.SSLError, socket.gaierror) as e:
            logging.warning(f"SMTP_SSL connection failed: {e}. Trying STARTTLS...")
            
            try:
                logging.info(f"Attempting STARTTLS connection to {smtp_server}:587")
                with smtplib.SMTP(smtp_server, 587, timeout=15) as server:
                    server.ehlo()
                    if server.has_extn('STARTTLS'):
                        server.starttls(context=context)
                        server.ehlo()
                    server.login(credentials['email'], credentials['password'])
                    server.send_message(msg)
                    logging.info('Email sent successfully via STARTTLS')
                    return True
            except Exception as starttls_error:
                logging.error(f"STARTTLS connection failed: {starttls_error}")
                raise Exception(f"Все методы подключения не сработали: {starttls_error}")
        except Exception as e:
            logging.error(f"SMTP error: {e}")
            raise Exception(f"Ошибка при отправке почты: {str(e)}")

        logging.info('Email with attachments sent successfully')
        return True
        
    except Exception as e:
        logging.error(f'Email failed to send: {e}')
        from i18n import _
        raise Exception(_('email_send_failed'))

def email_main(message: telebot.types.Message, bot: telebot.TeleBot, attachment: bool = 0, email_index=None):
    from i18n import _
    
    try:
        email_list = get_email_list()
        if not email_list:
            bot.send_message(message.from_user.id, _('email_not_configured'))
            return
            
        message_parts = []
        if not attachment:
            if hasattr(message, 'text') and message.text is not None:
                message_parts = message.text.split(' ')
        else:
            if hasattr(message, 'caption') and message.caption is not None:
                message_parts = message.caption.split(' ')
            
        try:
            credentials = get_email_credentials(email_index)
        except ValueError as e:
            bot.send_message(message.from_user.id, f"Ошибка конфигурации почты: {str(e)}")
            return
        
        if len(message_parts) < 2:
            try:
                emails = emails_list(email_index)
                if not emails:
                    bot.send_message(message.from_user.id, _('email_no_messages'))
                    return

                markup = types.InlineKeyboardMarkup(row_width=1)
                
                for index, email_item in enumerate(emails):
                    subject = email_item['Subject']
                    if len(subject) > 50:
                        subject = subject[:47] + "..."
                    
                    button_text = f"📧 {index + 1}. {subject[:47]}..." if len(subject) > 20 else f"📧 {index + 1}. {subject}"
                    callback_data = f"email_read_{index}" if email_index is None else f"email_read_{email_index}_{index}"
                    markup.add(types.InlineKeyboardButton(button_text, callback_data=callback_data))
                
                bot.send_message(
                    message.chat.id,
                    _('email_list_title').format(email='`' + credentials['email'] + '`'),
                    parse_mode="Markdown",
                    reply_markup=markup
                )
            except Exception as e:
                logging.error(f'Error getting emails: {e}')
                bot.send_message(message.from_user.id, _('email_list_error'))
            return
        
        try:
            current_directory = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            template = os.path.join(current_directory, 'data', 'email.html')
            
            if not os.path.exists(template):
                logging.error(f"Email template not found at {template}")
                bot.send_message(message.from_user.id, _('email_template_not_found'))
                return

            if attachment:
                file_info = bot.get_file(message.document.file_id)
                downloaded_file = bot.download_file(file_info.file_path)

                save_path = os.path.join(current_directory, message.document.file_name)
                os.makedirs(os.path.dirname(save_path), exist_ok=True)

                with open(save_path, 'wb') as new_file:
                    new_file.write(downloaded_file)

                send_email(message_parts[1], ' '.join(message_parts[2:]), template, save_path, email_index)
                os.remove(save_path)
            else:
                send_email(message_parts[1], ' '.join(message_parts[2:]), template, "", email_index)
            
            bot.send_message(message.from_user.id, _('email_sent_success'))
        except Exception as e:
            logging.error(f'Error sending email: {e}')
            bot.send_message(message.from_user.id, _('email_error'))
    except Exception as e:
        logging.error(f'Error in email_main: {e}')
        bot.send_message(message.from_user.id, _('email_error'))

def send_email(to_address: str, subject: str, template_path: str, attachment_path: str = "", email_index=None):
    try:
        credentials = get_email_credentials(email_index)
        
        with open(template_path, 'r', encoding='utf-8') as file:
            email_content = file.read()

        email_content = email_content.replace('{{message}}', subject)

        msg = MIMEMultipart()
        msg['From'] = credentials['email']
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

        logging.info(f"Connecting to SMTP server {credentials['smtp']} as {credentials['email']}")
        
        try:
            with smtplib.SMTP_SSL(credentials['smtp'], 465) as server:
                server.login(credentials['email'], credentials['password'])
                server.send_message(msg)
        except socket.gaierror as e:
            logging.error(f"DNS resolution failed for SMTP server {credentials['smtp']}: {e}")
            raise Exception(f"Не удалось подключиться к SMTP серверу: {str(e)}")
        except Exception as e:
            logging.error(f"SMTP error: {e}")
            raise Exception(f"Ошибка при отправке почты: {str(e)}")

        logging.info('Email sent successfully')
    except Exception as e:
        logging.error(f'Email failed to send: {e}')
        from i18n import _
        raise Exception(_('email_send_failed'))

def emails_list(email_index=None):
    emails = []
    try:
        credentials = get_email_credentials(email_index)
        
        if not credentials['imap'] or credentials['imap'].strip() == '':
            logging.error(f'Empty IMAP server for email {credentials["email"]}')
            return emails
        
        logging.info(f"Connecting to IMAP server: {credentials['imap']} with user {credentials['email']}")
        
        try:
            mail = imaplib.IMAP4_SSL(credentials['imap'])
        except socket.gaierror as e:
            logging.error(f"DNS resolution failed for {credentials['imap']}: {e}")
            return emails
        except Exception as e:
            logging.error(f"Failed to connect to IMAP server {credentials['imap']}: {e}")
            return emails
            
        try:
            mail.login(credentials['email'], credentials['password'])
        except imaplib.IMAP4.error as e:
            logging.error(f"IMAP login failed for {credentials['email']}: {e}")
            return emails
        except Exception as e:
            logging.error(f"Failed to login to {credentials['email']} on {credentials['imap']}: {e}")
            return emails
            
        mail.select('inbox')

        status, messages = mail.search(None, 'ALL')
        if status != 'OK':
            logging.error(f"Failed to search emails: {status}")
            return emails
            
        email_ids = messages[0].split()
        if not email_ids:
            logging.info("No emails found")
            return emails

        last_10_email_ids = email_ids[-10:] if len(email_ids) > 10 else email_ids
        last_10_email_ids.reverse() 

        for email_id in last_10_email_ids:
            try:
                status, msg_data = mail.fetch(email_id, '(RFC822)')
                if status != 'OK':
                    logging.error(f"Failed to fetch email {email_id}: {status}")
                    continue
                    
                for response_part in msg_data:
                    if isinstance(response_part, tuple):
                        msg = email.message_from_bytes(response_part[1])
                        subject = "No Subject"
                        
                        if msg['Subject']:
                            subject_header = decode_header(msg['Subject'])[0]
                            subject, encoding = subject_header
                            if isinstance(subject, bytes):
                                subject = subject.decode(encoding if encoding else 'utf-8', errors='replace')
                                
                        from_ = msg.get('From', 'Unknown Sender')

                        emails.append({
                            'From': from_,
                            'Subject': subject
                        })
            except Exception as e:
                logging.error(f"Error processing email {email_id}: {e}")
                continue

        mail.logout()
    except Exception as e:
        logging.error(f'Error in emails_list: {e}')
    
    return emails

def email_read_body(num: int, email_index=None):
    try:
        credentials = get_email_credentials(email_index)
        
        if not credentials['imap'] or credentials['imap'].strip() == '':
            raise ValueError(f'Empty IMAP server for email {credentials["email"]}')
        
        try:
            mail = imaplib.IMAP4_SSL(credentials['imap'])
        except socket.gaierror as e:
            logging.error(f"DNS resolution failed for {credentials['imap']}: {e}")
            raise ValueError(f"Unable to resolve IMAP server: {str(e)}")
            
        try:
            mail.login(credentials['email'], credentials['password'])
        except imaplib.IMAP4.error as e:
            logging.error(f"IMAP login failed for {credentials['email']}: {e}")
            raise ValueError(f"Login failed: {str(e)}")
            
        mail.select('inbox')

        status, messages = mail.search(None, 'ALL')
        if status != 'OK':
            raise ValueError(f"Failed to search emails: {status}")
            
        email_ids = messages[0].split()
        if not email_ids:
            raise ValueError("No emails found")

        last_10_email_ids = email_ids[-10:] if len(email_ids) > 10 else email_ids
        last_10_email_ids.reverse()
        
        if num < len(last_10_email_ids):
            email_id = last_10_email_ids[num]
        else:
            raise ValueError(f"Email index {num} out of range")

        status, msg_data = mail.fetch(email_id, '(RFC822)')
        if status != 'OK':
            raise ValueError(f"Failed to fetch email {email_id}: {status}")
            
        for response_part in msg_data:
            if isinstance(response_part, tuple):
                msg = email.message_from_bytes(response_part[1])
                subject = "No Subject"
                
                if msg['Subject']:
                    subject_header = decode_header(msg['Subject'])[0]
                    subject, encoding = subject_header
                    if isinstance(subject, bytes):
                        subject = subject.decode(encoding if encoding else 'utf-8', errors='replace')
                        
                from_ = msg.get('From', 'Unknown Sender')
                body = ''
                attachments = []

                if msg.is_multipart():
                    for part in msg.walk():
                        content_type = part.get_content_type()
                        content_disposition = str(part.get('Content-Disposition'))

                        if 'attachment' not in content_disposition and content_type in ['text/plain', 'text/html']:
                            try:
                                payload = part.get_payload(decode=True)
                                if payload:
                                    charset = part.get_content_charset() or 'utf-8'
                                    body += payload.decode(charset, errors='replace')
                            except Exception as e:
                                logging.error(f"Error decoding email part: {e}")
                                body += "[Content could not be decoded]"
                        
                        elif 'attachment' in content_disposition or 'inline' in content_disposition or content_type.startswith('application/'):
                            try:
                                filename = part.get_filename()
                                if filename:
                                    if isinstance(filename, str):
                                        try:
                                            if '=' in filename and '?' in filename:
                                                filename_parts = decode_header(filename)
                                                filename = ''
                                                for content, charset in filename_parts:
                                                    if isinstance(content, bytes):
                                                        filename += content.decode(charset or 'utf-8', 'replace')
                                                    else:
                                                        filename += content
                                        except Exception as e:
                                            logging.error(f"Error decoding filename: {e}")
                                    
                                    safe_filename = "".join(c for c in filename if c.isalnum() or c in "._- ")
                                    if not safe_filename:
                                        safe_filename = f"attachment_{len(attachments)}"
                                    os.makedirs('/tmp/email_attachments', exist_ok=True)
                                    
                                    file_path = f"/tmp/email_attachments/{safe_filename}"
                                    payload = part.get_payload(decode=True)
                                    if payload:
                                        with open(file_path, 'wb') as f:
                                            f.write(payload)
                                        
                                        attachments.append({
                                            'path': file_path,
                                            'name': safe_filename,
                                            'type': content_type
                                        })
                                        logging.info(f"Saved attachment: {safe_filename}, type: {content_type}")
                            except Exception as e:
                                logging.error(f"Error saving attachment: {e}")
                else:
                    try:
                        payload = msg.get_payload(decode=True)
                        if payload:
                            charset = msg.get_content_charset() or 'utf-8'
                            body = payload.decode(charset, errors='replace')
                    except Exception as e:
                        logging.error(f"Error decoding email body: {e}")
                        body = "[Content could not be decoded]"

                mail.logout()
                return {
                    'From': from_,
                    'Subject': subject,
                    'Body': body,
                    'Attachments': attachments
                }
        
        mail.logout()
        raise ValueError("Email content not found")
    except Exception as e:
        logging.error(f'Error in email_read_body: {e}')
        from i18n import _
        raise Exception(_('email_read_error'))

def email_read(message, bot: telebot.TeleBot):
    from i18n import _
    
    try:
        if isinstance(message, types.CallbackQuery):
            parts = message.data.split('_')
            if len(parts) == 4:
                email_index = int(parts[2])
                message_index = int(parts[3])
            else:
                email_index = None
                message_index = int(parts[2])
            
            user_id = message.from_user.id
            bot.answer_callback_query(message.id)
        else:
            parts = message.text.split('_')
            if len(parts) == 4:
                email_index = int(parts[2])
                message_index = int(parts[3])
            else:
                email_index = None
                message_index = int(parts[2])
                
            user_id = message.from_user.id
        
        bot.send_message(user_id, _('email_reading'))
        
        email_data = email_read_body(message_index, email_index)
        email_html = f"<h1>{email_data['From']}</h1><h2>{email_data['Subject']}</h2>{email_data['Body']}"
        pdf_path = f"/tmp/email_{user_id}_{message_index}.pdf"
        
        try:
            HTML(string=email_html).write_pdf(pdf_path)
            
            with open(pdf_path, 'rb') as pdf_file:
                bot.send_document(user_id, pdf_file, caption=f"📧 {email_data['Subject']}")
            os.remove(pdf_path)
            
            attachments = email_data.get('Attachments', [])
            if attachments:
                if len(attachments) == 1:
                    bot.send_message(user_id, _('email_has_one_attachment'))
                else:
                    bot.send_message(user_id, _('email_has_multiple_attachments').format(count=len(attachments)))
                
                media_group = []
                other_attachments = []
                
                for attachment in attachments:
                    file_path = attachment['path']
                    file_type = attachment['type']
                    
                    if file_type.startswith('image/'):
                        with open(file_path, 'rb') as f:
                            media_group.append(telebot.types.InputMediaPhoto(f.read(), caption=attachment['name']))
                    elif file_type.startswith('video/'):
                        with open(file_path, 'rb') as f:
                            media_group.append(telebot.types.InputMediaVideo(f.read(), caption=attachment['name']))
                    else:
                        other_attachments.append(file_path)
                
                if media_group:
                    bot.send_media_group(user_id, media_group)
                
                for file_path in other_attachments:
                    with open(file_path, 'rb') as f:
                        bot.send_document(user_id, f, caption=os.path.basename(file_path))
                
                for attachment in attachments:
                    try:
                        os.remove(attachment['path'])
                    except Exception as e:
                        logging.error(f"Error deleting attachment {attachment['path']}: {e}")
                
        except Exception as e:
            logging.error(f"Error creating PDF or sending attachments: {e}")
            bot.send_message(user_id, f"*От:* {email_data['From']}\n*Тема:* {email_data['Subject']}\n\n{email_data['Body'][:3000]}...", parse_mode="Markdown")
            
            attachments = email_data.get('Attachments', [])
            if attachments:
                for attachment in attachments:
                    try:
                        with open(attachment['path'], 'rb') as f:
                            bot.send_document(user_id, f, caption=attachment['name'])
                        os.remove(attachment['path'])
                    except Exception as attach_err:
                        logging.error(f"Error sending attachment {attachment['path']}: {attach_err}")
            
    except Exception as e:
        logging.error(f"Error in email_read: {e}")
        user_id = message.from_user.id if isinstance(message, telebot.types.Message) else message.from_user.id
        bot.send_message(user_id, _('email_read_error'))