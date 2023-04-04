from incidentrepo import IncidentRepository
import email, smtplib, ssl
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

sender_email = "no-reply@chevron.com"
receiver_email = "aldrinazupardo@chevron.com"

class NetworkTriage(object):
    """Class to represent network switches and routers"""
    
    def __init__(self, netWorkDevice):
        self.networkDevice =  netWorkDevice

    def operate(self) -> dict:
        pass

    def put_incident(self, params):
        self.networkDevice.put_incident(params=params)

    def send_email(subject, body):
        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = receiver_email
        message["Subject"] = subject
        message.attach(MIMEText(body, "plain"))
        text = message.as_string()
        context = ssl.create_default_context()
        with smtplib.SMTP('hou150.mox-mx.chevron.net', 25) as server:
            server.sendmail(sender_email, receiver_email, text)