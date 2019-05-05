import smtplib
import ssl
import warnings
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from enum import Enum
from typing import List

from . import Engine
from .. import DeliveryNotMade


class SMTPError(DeliveryNotMade):
    pass


class SMTPSecurity(Enum):
    NONE = 'None'
    SSL = 'SSL'
    START_TLS = 'StartTLS'


class SMTPDeliveryEngine(Engine):
    def __init__(self, host: str, port: int, security: SMTPSecurity, username: str = None, password: str = None):
        """
        SMTP delivery engine for templatemail. NOTE: This feature is not fully tested and SMTP is easy to get wrong.
        The developer has not fully tested this engine, so verify it works well for your server before proceeding.

        :param host: Host to connect to
        :param port: Port (there is no default because there are so many SMTP ports, you need to just get this right.)
        :param security: Security to use. One of SMTPSecurity.
        :param username: Username to use. Defaults to None, in which case a login is not attempted.
        :param password: Password to use, in conjunction with username
        """
        self.host = host
        self.port = port
        self.security = security
        self.username = username
        self.password = password

        warnings.warn('SMTPDeliveryEngine is a new and not thoroughly tested feature of templatemail.')

    def send_simple_message(self, from_address: str, to_addresses: List[str], subject: str, text_body: str = None,
                            html_body: str = None):
        args = dict(from_address=from_address,
                    to_addresses=to_addresses,
                    subject=subject,
                    text_body=text_body,
                    html_body=html_body)

        if self.security == SMTPSecurity.START_TLS:
            self._send_simple_message_start_tls(**args)
        elif self.security == SMTPSecurity.SSL:
            self._send_simple_message_ssl(**args)
        elif self.security == SMTPSecurity.NONE:
            self._send_simple_message_no_security(**args)
        else:
            raise ValueError('Unexpected security: %r' % self.security)

    def _send_simple_message_start_tls(self, from_address: str, to_addresses: List[str], subject: str,
                                       text_body: str = None, html_body: str = None):
        context = ssl.create_default_context()

        server = smtplib.SMTP(self.host, self.port)
        server.ehlo()
        server.starttls(context=context)
        server.ehlo()
        self._login_with_server(server)

        self._do_delivery_with_server(server=server,
                                      from_address=from_address,
                                      to_addresses=to_addresses,
                                      subject=subject,
                                      text_body=text_body,
                                      html_body=html_body)

    def _send_simple_message_no_security(self, from_address: str, to_addresses: List[str], subject: str,
                                         text_body: str = None, html_body: str = None):
        context = ssl.create_default_context()

        server = smtplib.SMTP(self.host, self.port)
        server.ehlo()
        self._login_with_server(server)

        self._do_delivery_with_server(server=server,
                                      from_address=from_address,
                                      to_addresses=to_addresses,
                                      subject=subject,
                                      text_body=text_body,
                                      html_body=html_body)

    def _send_simple_message_ssl(self, from_address: str, to_addresses: List[str], subject: str, text_body: str = None,
                                 html_body: str = None):
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(self.host, self.port, context=context) as server:
            self._login_with_server(server)
            self._do_delivery_with_server(server=server,
                                          from_address=from_address,
                                          to_addresses=to_addresses,
                                          subject=subject,
                                          text_body=text_body,
                                          html_body=html_body)

    def _login_with_server(self, server):
        if self.username and self.password:
            server.login(self.username, self.password)

    def _do_delivery_with_server(self, server: smtplib.SMTP, from_address: str, to_addresses: List[str], subject: str,
                                 text_body: str = None, html_body: str = None):
        if html_body and text_body:
            msg = MIMEMultipart('alternative')
            msg.attach(MIMEText(text_body, "plain"))
            msg.attach(MIMEText(html_body, "html"))
        elif html_body:
            msg = MIMEMultipart('alternative')
            msg.attach(MIMEText(html_body, "html"))
        elif text_body:
            msg = MIMEText(text_body)
        else:
            raise ValueError('You must specify html, text, or both.')
        msg['Subject'] = subject
        msg['From'] = from_address
        msg['To'] = ", ".join(to_addresses)
        server.sendmail(from_address, to_addresses, msg.as_string())


__all__ = ['SMTPDeliveryEngine', 'SMTPSecurity', 'SMTPError']
