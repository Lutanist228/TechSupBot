import csv
import smtplib
import imaplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import Header
import email
from email.parser import Parser
from email.policy import default
from pprint import pprint

class DataParser():
    def __init__(self, path: str, format: str) -> None:
        self.path = path
        self.format = format
        
    def read_info(self):
        data = []
        
        with open(self.path, "r", encoding="utf-8") as file:
            match self.format:
                case "csv":
                    reader = csv.DictReader(file)
                    for row in reader:
                        data.append(row)
                    return data
        
class DataTypeError():
    def __init__(self, error_message: str) -> None:
        self.raise_error(error_message)
        
    def raise_error(error_message: str) -> None:
        return print(error_message)
        
class MailSender():
    def __init__(self, receiver: str, sender: str, letter_text: str, password: str, subject: str = None) -> None:
        self.sender = sender
        self.password = password 
        self.receiver = receiver 
        self.subject = subject
        self.letter_text = letter_text
        self.message = None
        self.server = None
        
    def connect(self, port: int = 465, timeout: int = 10) -> smtplib.SMTP_SSL:
        try:
            server = smtplib.SMTP_SSL('smtp.yandex.com', port, timeout=timeout)
            server.login(self.sender, self.password)
            self.server = server
        except Exception as e:
            print("Ошибка подключения -", e)
            print("Попытка повторного подключения к серверу...")
            self.connect(port=port, timeout=timeout)
        
        return self
        
    def close_connection(self):
        self.server.close()    
        
    def create_message(self) -> MIMEText:
        message = (MIMEText(self.letter_text, "plain", "utf-8"))
        message["From"] = self.sender
        message["To"] = self.receiver
        message["Subject"] = Header(self.subject, "utf-8") # id телеграмма
        
        self.message = message
    
    def send_email(self) -> None:
        self.server.sendmail(self.sender, self.receiver, self.message.as_string())
        print(f"Письмо было успешно отправлено по адресу {self.receiver} от {self.sender}")
            
class MailParser():
    def __init__(self, mail_login: str, mail_password: str) -> None:
        self.mail_login = mail_login
        self.mail_password = mail_password 
        self.server = None   
        
    def connect(self, port: int = 993, timeout: int = 10) -> imaplib.IMAP4_SSL:
        try:
            server = imaplib.IMAP4_SSL('imap.yandex.com', port, timeout=timeout)
            server.login(self.mail_login, self.mail_password)
            self.server = server
        except Exception as e:
            print("Ошибка подключения -", e)
            print("Попытка повторного подключения к серверу...")
            self.connect(port=port, timeout=timeout)
        
        return self
        
    def close_connection(self):
        self.server.close()    
        
    def return_section_data(self, section: str = "INBOX") -> tuple:
        self.server.select(section)
        status, data = self.server.search(None, "ALL")
        
        id_list = data[0] ; id_list = id_list.split()
        id_list = list(map(lambda x: x.decode('utf-8'), id_list))
        
        return status, id_list
    
    def return_msg_data(self, msg_id: int) -> dict:
        message = dict()
        
        result, data = self.server.fetch(msg_id, "(RFC822)")
        raw_email = data[0][1]
        raw_email_string = raw_email.decode('utf-8')
        email_message = email.message_from_string(raw_email_string)
        
        headers = Parser(policy=default).parsestr(raw_email_string)
        body = headers.get_body(preferencelist=('plain', 'html'))
            
        message.update([('From', headers['from'])])
        message.update([('To', headers['to'])])
        message.update([('Date', email_message['Date'])])
        message.update([('Subject', headers['subject'])])
        message.update([('Content', ''.join(body.get_content().splitlines(keepends=False)[:3]))])
        message.update([('Message-Id', email_message['Message-Id'])])
        message.update([('Message-Number', int(msg_id))])

        pprint(message, sort_dicts=False)
        
        return message
   